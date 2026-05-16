#!/usr/bin/env python3
"""boot_check.py — verify MVS boots and JES2 becomes active.

Usage:
    python emulator/scripts/boot_check.py /path/to/emulator/mvs/mvs-tk5
    # or set HERCULES_MVS_PATH and call with no args:
    HERCULES_MVS_PATH=/path/to/emulator/mvs/mvs-tk5 python emulator/scripts/boot_check.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path


def _to_windows_path(p: str) -> Path:
    """Convert Git Bash /c/Users/... style paths to Windows C:/Users/... paths."""
    m = re.match(r"^/([a-zA-Z])/(.*)", p)
    if m:
        return Path(f"{m.group(1).upper()}:\\{m.group(2).replace('/', os.sep)}")
    return Path(p)

# TK4-:  $HASP100 JES2 IS ACTIVE
# TK5:   $HASP493 JES2  QUICK-START IS IN PROGRESS  (JES2 dispatch confirmed)
_JES2_READY_PATTERNS = [
    "$HASP100 JES2 IS ACTIVE",        # TK4-
    "$HASP493 JES2",                   # TK5 quick-start
    "$HASP100 BSPPILOT ON STCINRDR",  # TK5 fallback — first started task
]
_JES2_READY = _JES2_READY_PATTERNS  # backward-compat alias
_BOOT_TIMEOUT = 180  # seconds — TK5 takes ~90-120s on first boot
_DASD_WAIT_TIMEOUT = 60  # seconds to wait for AV scanner to release DASD files


def _wait_for_dasd(mvs_path: Path, timeout: int = _DASD_WAIT_TIMEOUT) -> None:
    """Wait until the primary DASD file is not locked (e.g., by AV scanner).

    Windows AV scanners briefly lock DASD files after each Hercules shutdown.
    Attempting to boot Hercules while locked yields HHC00404E Permission denied.
    """
    dasd = mvs_path / "dasd" / "tk5res.390"
    if not dasd.exists():
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with open(dasd, "r+b") as fh:
                fh.read(1)
            return  # accessible — proceed
        except (PermissionError, OSError):
            sys.stdout.write("~")
            sys.stdout.flush()
            time.sleep(2)
    print()  # newline after any ~ dots


def main() -> int:
    mvs_path_str = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("HERCULES_MVS_PATH")
    )
    if not mvs_path_str:
        print(
            "ERROR: supply MVS path as argument or set HERCULES_MVS_PATH",
            file=sys.stderr,
        )
        return 1

    mvs_path = _to_windows_path(mvs_path_str).resolve()
    if not mvs_path.exists():
        print(f"ERROR: MVS path not found: {mvs_path}", file=sys.stderr)
        return 1

    # Detect TK5 vs custom template
    tk5_conf = mvs_path / "conf" / "tk5.cnf"
    if tk5_conf.exists():
        return _boot_tk5(mvs_path, tk5_conf)
    else:
        return _boot_template(mvs_path)


def _boot_tk5(mvs_path: Path, conf: Path) -> int:
    """Boot using TK5's own config — run hercules from the TK5 root directory."""
    log_path = mvs_path / "log" / "3033.log"
    (mvs_path / "log").mkdir(exist_ok=True)

    # Prefer TK5's bundled Hercules if present, else fall back to PATH
    bundled = mvs_path / "hercules" / "windows" / "64" / "hercules.exe"
    herc_exe = str(bundled) if bundled.exists() else "hercules"

    env = os.environ.copy()
    # intcons (default) = 0009 3215-C, the unattended console; extcons requires a live 3270 session
    env.pop("TK5CONS", None)
    env["TK5CRLF"] = "CRLF"

    # Prepend a HASP479 auto-reply to the standard ipl.rc.  On first boot (or after
    # an unclean shutdown) JES2 issues WTOR $HASP479 asking Y/N for the CKPT lock;
    # without an auto-reply Hercules times out and JES2 never becomes active.
    rc_file = mvs_path / "_zopt_boot.rc"
    rc_file.write_text(
        "hao tgt HASP479\nhao cmd /r 00,y\nscript scripts/ipl.rc\n",
        encoding="utf-8",
    )
    env["HERCULES_RC"] = "_zopt_boot.rc"

    _wait_for_dasd(mvs_path)
    print(f"Starting Hercules from {mvs_path} (timeout: {_BOOT_TIMEOUT}s) ...")

    try:
        with open(log_path, "w", encoding="utf-8", errors="replace") as log_fh:
            proc = subprocess.Popen(
                [herc_exe, "-d", "-f", "conf/tk5.cnf"],  # -d = daemon (non-interactive), relative conf
                cwd=str(mvs_path),
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                env=env,
            )
            try:
                found = _wait_for_jes2(log_path)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
    finally:
        rc_file.unlink(missing_ok=True)

    if found:
        print("MVS UP · JES2 ACTIVE")
        return 0

    print(f"\nERROR: JES2 did not become active within {_BOOT_TIMEOUT}s")
    _print_log_tail(log_path, n=40)
    return 1


def _boot_template(mvs_path: Path) -> int:
    """Boot using our custom hercules_template.conf (TK4- layout)."""
    import tempfile

    template = Path("emulator/config/hercules_template.conf")
    if not template.exists():
        print(f"ERROR: config template not found: {template}", file=sys.stderr)
        return 1

    conf_text = template.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="zopt_boot_") as _workdir:
        workdir = Path(_workdir)
        (workdir / "dasd").mkdir(exist_ok=True)
        (workdir / "shadows").mkdir(exist_ok=True)

        conf_text_resolved = (
            conf_text
            .replace("{{MVS_PATH}}", str(mvs_path))
            .replace("{{WORKDIR}}", str(workdir))
            .replace("{{CNSLPORT}}", "3270")
            .replace("{{HTTPPORT}}", "8081")
        )
        conf_path = workdir / "hercules.conf"
        conf_path.write_text(conf_text_resolved, encoding="utf-8")

        log_path = workdir / "hercules.log"
        print(f"Starting Hercules (timeout: {_BOOT_TIMEOUT}s) ...")

        with open(log_path, "w", encoding="utf-8") as log_fh:
            proc = subprocess.Popen(
                ["hercules", "-f", str(conf_path)],
                cwd=str(workdir),
                stdout=log_fh,
                stderr=subprocess.STDOUT,
            )
            try:
                found = _wait_for_jes2(log_path)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()

    if found:
        print("MVS UP · JES2 ACTIVE")
        return 0

    print(f"\nERROR: JES2 did not become active within {_BOOT_TIMEOUT}s")
    _print_log_tail(log_path, n=30)
    return 1


def _wait_for_jes2(log_path: Path) -> bool:
    deadline = time.monotonic() + _BOOT_TIMEOUT
    while time.monotonic() < deadline:
        time.sleep(3)
        if log_path.exists():
            try:
                text = log_path.read_text(errors="replace")
                if any(pat in text for pat in _JES2_READY_PATTERNS):
                    return True
            except OSError:
                pass
        sys.stdout.write(".")
        sys.stdout.flush()
    print()
    return False


def _print_log_tail(log_path: Path, n: int = 40) -> None:
    if not log_path.exists():
        return
    try:
        lines = log_path.read_text(errors="replace").splitlines()
        print(f"\n--- last {n} lines of hercules log ---")
        for line in lines[-n:]:
            print(" ", line)
    except OSError:
        pass


if __name__ == "__main__":
    sys.exit(main())
