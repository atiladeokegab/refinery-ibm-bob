"""HerculesPool — manages N isolated HERCULES daemon processes for parallel RL use.

Each pool slot owns:
- A unique CNSLPORT (3270 + slot_id) and HTTPPORT (8081 + slot_id).
- Its own workdir with a base DASD image and a copy-on-write shadow file.
- A card-reader path that CardReader writes JCL into.

Shadow DASD reset (fast path):
    On release, the pool sends DETACH / ATTACH console commands via the
    Hercules HTTP API. The shadow file is deleted and recreated — the
    Hercules process stays running and MVS does not re-IPL. Reset time is
    O(shadow file size), typically < 1 second, vs. 60-90 s for a full boot.

Fallback (slow path):
    If the HTTP console is unreachable (e.g. catastrophic ABEND that crashed
    Hercules), the pool restarts the process and copies the base DASD image.

Usage:
    with HerculesPool(n=4, base_conf=Path("emulator/config/hercules_template.conf"),
                      base_dasd=Path("emulator/config/dasd/scratch_base.img")) as pool:
        slot = pool.acquire()
        try:
            job_id = card_reader.submit(jcl, slot.card_reader_path)
            rc = spool_monitor.wait(job_id, slot.workdir)
        finally:
            pool.release(slot)
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_CNSLPORT_BASE = 3270
_HTTPPORT_BASE = 8081


@dataclass
class PoolSlot:
    slot_id:          int
    workdir:          Path
    conf_path:        Path
    base_dasd:        Path   # never written — source of truth
    shadow_dasd:      Path   # copy-on-write overlay, discarded on reset
    card_reader_path: Path
    http_port:        int
    process:          Optional[subprocess.Popen] = field(default=None, repr=False)

    @property
    def cnsl_port(self) -> int:
        return _CNSLPORT_BASE + self.slot_id

    @property
    def dasd_path(self) -> Path:
        """Backward-compatible alias — points at the shadow file."""
        return self.shadow_dasd


class HerculesPool:
    """Thread-safe pool of N isolated HERCULES processes with shadow DASD reset.

    Parameters
    ----------
    n:
        Number of parallel HERCULES slots.
    base_conf:
        Path to hercules config template. ``{{WORKDIR}}``, ``{{CNSLPORT}}``,
        and ``{{HTTPPORT}}`` are substituted per slot.
    base_dasd:
        Path to a clean scratch DASD image (never modified).
    """

    def __init__(self, n: int, base_conf: Path, base_dasd: Path) -> None:
        self._n         = n
        self._base_conf = Path(base_conf)
        self._base_dasd = Path(base_dasd)

        self._slots:   list[PoolSlot] = []
        self._free:    list[PoolSlot] = []
        self._lock     = threading.Lock()
        self._sem      = threading.Semaphore(0)
        self._started  = False

    # ── Context manager ───────────────────────────────────────────────────────

    def __enter__(self) -> "HerculesPool":
        self._start()
        return self

    def __exit__(self, *_) -> None:
        self._stop()

    # ── Public API ────────────────────────────────────────────────────────────

    def acquire(self) -> PoolSlot:
        """Block until a free slot is available and return it."""
        self._sem.acquire()
        with self._lock:
            return self._free.pop()

    def release(self, slot: PoolSlot) -> None:
        """Reset slot state and return it to the pool.

        Attempts fast shadow DASD reset via the Hercules HTTP console.
        Falls back to process restart + base DASD copy if the HTTP console
        is unreachable (e.g. catastrophic abend killed the Hercules process).
        """
        if not self._shadow_reset(slot):
            self._restart_slot(slot)
        with self._lock:
            self._free.append(slot)
        self._sem.release()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def _start(self) -> None:
        if self._started:
            return
        self._started = True
        base_conf_text = self._base_conf.read_text(encoding="utf-8")

        for i in range(self._n):
            workdir = Path(tempfile.mkdtemp(prefix=f"zopt_slot{i}_"))
            (workdir / "dasd").mkdir(exist_ok=True)

            base_dasd = workdir / "dasd" / "scratch_base.img"
            shadow_dasd = workdir / "dasd" / "scratch_shadow.img"
            if self._base_dasd.exists():
                shutil.copy2(self._base_dasd, base_dasd)

            http_port = _HTTPPORT_BASE + i
            conf_text = (
                base_conf_text
                .replace("{{WORKDIR}}", str(workdir))
                .replace("{{CNSLPORT}}", str(_CNSLPORT_BASE + i))
                .replace("{{HTTPPORT}}", str(http_port))
            )
            conf_path = workdir / "hercules.conf"
            conf_path.write_text(conf_text, encoding="utf-8")

            slot = PoolSlot(
                slot_id=i,
                workdir=workdir,
                conf_path=conf_path,
                base_dasd=base_dasd,
                shadow_dasd=shadow_dasd,
                card_reader_path=workdir / "reader.jcl",
                http_port=http_port,
                process=self._launch_daemon(conf_path, workdir),
            )
            self._slots.append(slot)
            self._free.append(slot)
            self._sem.release()

    def _stop(self) -> None:
        for slot in self._slots:
            self._kill_process(slot)
            shutil.rmtree(slot.workdir, ignore_errors=True)
        self._slots.clear()
        self._free.clear()
        self._started = False

    # ── Shadow DASD reset (fast path) ─────────────────────────────────────────

    def _shadow_reset(self, slot: PoolSlot) -> bool:
        """Reset DASD state without restarting Hercules.

        Sends DETACH 0200 via HTTP console, recreates the shadow file,
        then sends ATTACH 0200 to remount with a fresh shadow layer.
        Returns True on success, False if HTTP console is unreachable.
        """
        if not self._http_cmd(slot, "detach 0200"):
            return False
        try:
            slot.shadow_dasd.unlink(missing_ok=True)
        except OSError:
            return False
        cmd = (
            f"attach 0200 3390 {slot.base_dasd} {slot.shadow_dasd} autoformat"
        )
        return self._http_cmd(slot, cmd)

    def _http_cmd(self, slot: PoolSlot, cmd: str) -> bool:
        """Send a single Hercules console command via the HTTP API."""
        url = f"http://127.0.0.1:{slot.http_port}/?cmd={urllib.parse.quote(cmd)}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError):
            return False

    # ── Slow path — process restart ───────────────────────────────────────────

    def _restart_slot(self, slot: PoolSlot) -> None:
        """Full reset: kill Hercules, restore base DASD, relaunch."""
        self._kill_process(slot)
        if slot.base_dasd.exists():
            try:
                slot.shadow_dasd.unlink(missing_ok=True)
                shutil.copy2(slot.base_dasd, slot.base_dasd)  # no-op: base is pristine
            except OSError:
                pass
        slot.process = self._launch_daemon(slot.conf_path, slot.workdir)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _launch_daemon(self, conf_path: Path, workdir: Path) -> Optional[subprocess.Popen]:
        log_path = workdir / "hercules.log"
        try:
            log_fh = open(log_path, "w", encoding="utf-8")
            return subprocess.Popen(
                ["hercules", "-f", str(conf_path), "-daemon"],
                cwd=workdir,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
            )
        except (FileNotFoundError, OSError):
            return None

    def _kill_process(self, slot: PoolSlot) -> None:
        if slot.process is None or slot.process.poll() is not None:
            return
        try:
            slot.process.terminate()
            slot.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            slot.process.kill()
            slot.process.wait(timeout=5)
        except OSError:
            pass
