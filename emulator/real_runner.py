"""RealHerculesRunner — drop-in replacement for SyntheticRunner using a live
Hercules/MVS instance via HerculesPool, CardReader, SpoolMonitor, SMFExtractor.

Activated when HERCULES_MVS_PATH environment variable is set.
Falls back to SyntheticRunner automatically when the variable is absent
(handled in api/worker.py _make_env).

TK5 path (detected by presence of conf/tk5.cnf):
    Boots TK5 using its own conf, waits for JES2, submits jobs via the
    socket card reader (device 000C, port 3505).

Template path (legacy TK4- layout):
    Uses HerculesPool with our custom hercules_template.conf.
"""
from __future__ import annotations

import os
import socket as _socket
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from emulator.bridge.card_reader import CardReader
from emulator.bridge.jcl_bridge import JCLBridge
from emulator.bridge.spool_monitor import SpoolMonitor
from emulator.pool import HerculesPool
from emulator.smf.extractor import SMFExtractor
from emulator import smf_proxy

# JCL: compile + link-edit + run COBOL via COBUCG cataloged procedure.
# COBOL source is inlined after COB.SYSIN so no pre-upload step is needed.
_JCL_TEMPLATE = """\
//ZOPTJOB  JOB (ACCT),'REFINERY',CLASS=A,MSGCLASS=A,MSGLEVEL=(1,1)
//COBRUN   EXEC COBUCG
//COB.SYSIN DD *
{cobol_source}
/*
//GO.SYSOUT   DD SYSOUT=*
//GO.SYSPRINT DD SYSOUT=*
"""

# TK5 defaults
_TK5_HTTP_PORT   = 8038
_TK5_CARD_DEVICE = "010c"


# ── TK5-specific pool/slot wrappers ──────────────────────────────────────────

@dataclass
class _TK5Slot:
    card_reader_path: Path   # file CardReader writes JCL to
    workdir: Path            # directory SpoolMonitor scans (mvs_path/log)
    http_port: int
    card_reader_device: str
    mvs_root: Path


class _TK5Pool:
    """Minimal pool interface for a single live TK5 Hercules process."""

    def __init__(self, mvs_path: Path, http_port: int = _TK5_HTTP_PORT) -> None:
        self._mvs_path   = mvs_path
        self._http_port  = http_port
        self._proc: subprocess.Popen | None = None
        self._log_fh     = None
        self._we_started = False  # True only when we booted Hercules ourselves
        self._slot       = _TK5Slot(
            card_reader_path   = mvs_path / "rdr" / "job.jcl",
            workdir            = mvs_path / "log",
            http_port          = http_port,
            card_reader_device = _TK5_CARD_DEVICE,
            mvs_root           = mvs_path,
        )

    def _is_running(self) -> bool:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self._http_port}/", timeout=3
            ):
                return True
        except Exception:
            return False

    # ── Pool protocol ─────────────────────────────────────────────────────────

    def acquire(self) -> _TK5Slot:
        return self._slot

    def release(self, slot: _TK5Slot) -> None:
        pass  # single persistent instance — no slot reset needed

    def __enter__(self) -> "_TK5Pool":
        from emulator.scripts.boot_check import _wait_for_jes2, _wait_for_dasd

        log_dir  = self._mvs_path / "log"
        rdr_dir  = self._mvs_path / "rdr"
        log_dir.mkdir(exist_ok=True)
        rdr_dir.mkdir(exist_ok=True)

        # Attach to an already-running Hercules/JES2 instead of booting a second copy
        if self._is_running():
            self._we_started = False
            return self

        _wait_for_dasd(self._mvs_path)

        log_path = log_dir / "3033.log"

        bundled  = self._mvs_path / "hercules" / "windows" / "64" / "hercules.exe"
        herc_exe = str(bundled) if bundled.exists() else "hercules"

        env = os.environ.copy()
        env.pop("TK5CONS", None)
        env["TK5CRLF"] = "CRLF"

        # HASP479 auto-reply: on first boot or unclean shutdown JES2 asks Y/N
        rc_file = self._mvs_path / "_zopt_runner.rc"
        rc_file.write_text(
            "hao tgt HASP479\nhao cmd /r 00,y\nscript scripts/ipl.rc\n",
            encoding="utf-8",
        )
        env["HERCULES_RC"] = "_zopt_runner.rc"

        self._log_fh = open(log_path, "w", encoding="utf-8", errors="replace")
        self._proc   = subprocess.Popen(
            [herc_exe, "-d", "-f", "conf/tk5.cnf"],
            cwd=str(self._mvs_path),
            stdout=self._log_fh,
            stderr=subprocess.STDOUT,
            env=env,
        )
        self._we_started = True

        if not _wait_for_jes2(log_path):
            self.__exit__(None, None, None)
            try:
                rc_file.unlink(missing_ok=True)
            except OSError:
                pass
            raise RuntimeError("TK5 MVS did not come up within timeout")

        # Best-effort cleanup: Hercules may still hold the file open on Windows.
        try:
            rc_file.unlink(missing_ok=True)
        except OSError:
            pass
        return self

    def __exit__(self, *_) -> None:
        if not self._we_started:
            return  # attached to externally-managed Hercules; leave it running
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=15)
            except (subprocess.TimeoutExpired, OSError):
                try:
                    self._proc.kill()
                except OSError:
                    pass
            self._proc = None
        if self._log_fh is not None:
            try:
                self._log_fh.close()
            except OSError:
                pass
            self._log_fh = None


_TK5_READER_PORT = 3505   # device 000C socket card reader


class _TK5CardReader:
    """Submits JCL to TK5 via the socket card reader (device 000C, port 3505).

    TK5 JES2 is configured with a single reader (000C sockdev).  The
    file-based reader at 010C is not in JES2's reader pool, so devinit
    to 010C has no effect.  Socket submission is the confirmed path.
    """

    def submit(self, jcl: str, reader_path: Path) -> str:  # reader_path ignored
        job_id = CardReader()._extract_job_name(jcl)
        with _socket.create_connection(("127.0.0.1", _TK5_READER_PORT), timeout=10) as s:
            s.sendall(jcl.encode("ascii"))
        return job_id


# ── RealHerculesRunner ────────────────────────────────────────────────────────

class RealHerculesRunner:
    """Wraps a Hercules/MVS pool to expose the same .run() interface as SyntheticRunner.

    Parameters
    ----------
    pool:          Pool object with acquire() / release() — either HerculesPool or _TK5Pool.
    card_reader:   CardReader-compatible object.
    spool_monitor: SpoolMonitor — polls workdir logs for HASP395 completion.
    smf_extractor: SMFExtractor — reads telemetry from hercules.log.
    """

    def __init__(
        self,
        pool: Any,
        card_reader: Any,
        spool_monitor: SpoolMonitor,
        smf_extractor: SMFExtractor,
    ) -> None:
        self._pool          = pool
        self._card_reader   = card_reader
        self._spool_monitor = spool_monitor
        self._smf_extractor = smf_extractor
        self._baseline_mips: float | None = None
        self._tmp_conf: Path | None       = None

    @classmethod
    def from_mvs_path(cls, mvs_path: str | Path) -> "RealHerculesRunner":
        """Factory — auto-detects TK5 vs template layout from mvs_path."""
        mvs_path = Path(mvs_path)
        if (mvs_path / "conf" / "tk5.cnf").exists():
            return cls._from_tk5(mvs_path)
        return cls._from_template(mvs_path)

    @classmethod
    def _from_tk5(cls, mvs_path: Path) -> "RealHerculesRunner":
        """Boot TK5 using its native config, wait for JES2, wire components."""
        pool = _TK5Pool(mvs_path)
        pool.__enter__()
        slot = pool._slot

        bridge = JCLBridge(mvs_path=mvs_path)

        runner = cls(
            pool          = pool,
            card_reader   = _TK5CardReader(),
            spool_monitor = SpoolMonitor(poll_interval=1.0),
            smf_extractor = SMFExtractor(hercules_runner=None, jcl_bridge=bridge),
        )
        return runner

    @classmethod
    def _from_template(cls, mvs_path: Path) -> "RealHerculesRunner":
        """Legacy: boot via HerculesPool + our custom hercules_template.conf."""
        template   = Path("emulator/config/hercules_template.conf")
        conf_text  = template.read_text(encoding="utf-8")
        conf_text  = conf_text.replace("{{MVS_PATH}}", str(mvs_path))

        tmp = tempfile.NamedTemporaryFile(
            suffix=".conf", mode="w", delete=False, encoding="utf-8",
            prefix="zopt_herc_",
        )
        tmp.write(conf_text)
        tmp.close()
        resolved_conf = Path(tmp.name)

        base_dasd = mvs_path / "dasd" / "work0.3350"
        pool      = HerculesPool(n=1, base_conf=resolved_conf, base_dasd=base_dasd)
        pool.__enter__()

        runner = cls(
            pool          = pool,
            card_reader   = CardReader(),
            spool_monitor = SpoolMonitor(poll_interval=0.5),
            smf_extractor = SMFExtractor(hercules_runner=None, jcl_bridge=None),
        )
        runner._tmp_conf = resolved_conf
        return runner

    def run(self, cobol_path: str | Path) -> dict:
        """Run one COBOL program and return telemetry matching SyntheticRunner.run()."""
        cobol_source = Path(cobol_path).read_text(encoding="utf-8", errors="replace")
        jcl          = _JCL_TEMPLATE.format(cobol_source=cobol_source)

        bridge = self._smf_extractor._bridge

        slot = self._pool.acquire()
        try:
            # Activate PRINTER1 so MSGCLASS=A JOBLOG (IEF376I real CPU time) lands in prt00e.txt
            if bridge is not None:
                bridge.setup_printer()

            t0     = time.monotonic()
            job_id = self._card_reader.submit(jcl, slot.card_reader_path)
            rc     = self._spool_monitor.wait(job_id, slot.workdir, timeout=180)
            wall_us = int((time.monotonic() - t0) * 1_000_000)

            # For TK5 the primary log is workdir/3033.log; for pool it's hercules.log
            log_candidates = [
                slot.workdir / "3033.log",
                slot.workdir / "hercules.log",
            ]
            raw_output = ""
            for lp in log_candidates:
                if lp.exists():
                    raw_output = lp.read_text(errors="replace")
                    break

            # Read IEF376I real CPU time from JOBLOG before IFASMFDP Phase II clears the printer
            ief_cpu_us = 0
            if bridge is not None:
                prt_text   = bridge.wait_for_print()
                ief_cpu_us = self._smf_extractor.parse_ief376i(prt_text, "ZOPTJOB")

            if ief_cpu_us > 0:
                # IEF376I gave us real CPU time — skip IFASMFDP Phase II entirely to
                # avoid polluting prt00e.txt and wasting a job submission per step.
                telemetry = {
                    "cpu_time_us":     ief_cpu_us,
                    "elapsed_time_us": ief_cpu_us,
                    "excp_count":      0,
                    "mips_estimate":   0.0,
                    "return_code":     0,
                }
            else:
                telemetry = self._smf_extractor.extract_to_state_dict(raw_output)

            # Fall back to Python wall-clock timing when SMF records are absent
            if telemetry["elapsed_time_us"] == 0 and wall_us > 0:
                telemetry["elapsed_time_us"] = wall_us
                telemetry["cpu_time_us"]     = wall_us
        finally:
            self._pool.release(slot)

        elapsed_s = telemetry["elapsed_time_us"] / 1_000_000
        mips      = smf_proxy.instructions_to_mips(
            telemetry["cpu_time_us"], max(elapsed_s, 0.001)
        )
        if self._baseline_mips is None:
            self._baseline_mips = mips

        return {
            "instruction_count":    telemetry["cpu_time_us"],
            "elapsed_cycles":       elapsed_s,
            "memory_pages_touched": telemetry["excp_count"] // 400,
            "exit_code":            0 if rc == 0 else 1,
        }

    def __del__(self) -> None:
        try:
            self._pool.__exit__(None, None, None)
        except Exception:
            pass
        if self._tmp_conf and self._tmp_conf.exists():
            try:
                self._tmp_conf.unlink()
            except OSError:
                pass
