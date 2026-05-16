#!/usr/bin/env python3
"""live_job_test.py — boot TK5, submit a real COBOL job, print output.

Usage:
    python emulator/scripts/live_job_test.py C:\\path\\to\\mvs-tk5
    # or
    HERCULES_MVS_PATH=C:\\path\\to\\mvs-tk5 python emulator/scripts/live_job_test.py
"""
from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# -- reuse path helper and JES2 patterns from boot_check --------------------

def _to_windows_path(p: str) -> Path:
    m = re.match(r"^/([a-zA-Z])/(.*)", p)
    if m:
        return Path(f"{m.group(1).upper()}:\\{m.group(2).replace('/', os.sep)}")
    return Path(p)

_JES2_READY_PATTERNS = [
    "$HASP100 JES2 IS ACTIVE",
    "$HASP493 JES2",
    "$HASP100 BSPPILOT ON STCINRDR",
]
_BOOT_TIMEOUT   = 180
_JOB_TIMEOUT    = 120
_JOB_NAME       = "ZOPTJOB"
_READER_PORT    = 3505
_HTTP_PORT      = 8038   # TK5 default Hercules HTTP API port

_JCL = """\
//ZOPTJOB  JOB (ACCT),'REFINERY',CLASS=A,MSGCLASS=A,MSGLEVEL=(1,1)
//COBRUN   EXEC COBUCG
//COB.SYSIN DD *
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       PROCEDURE DIVISION.
           DISPLAY 'HELLO FROM REAL MVS'.
           STOP RUN.
/*
//GO.SYSOUT   DD SYSOUT=A
//GO.SYSPRINT DD SYSOUT=A
"""


def main() -> int:
    mvs_path_str = (
        sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HERCULES_MVS_PATH")
    )
    if not mvs_path_str:
        print("ERROR: supply MVS path as argument or HERCULES_MVS_PATH", file=sys.stderr)
        return 1

    mvs_path = _to_windows_path(mvs_path_str).resolve()
    if not mvs_path.exists():
        print(f"ERROR: path not found: {mvs_path}", file=sys.stderr)
        return 1

    bundled = mvs_path / "hercules" / "windows" / "64" / "hercules.exe"
    herc_exe = str(bundled) if bundled.exists() else "hercules"

    log_path = mvs_path / "log" / "3033.log"
    (mvs_path / "log").mkdir(exist_ok=True)
    (mvs_path / "prt").mkdir(exist_ok=True)

    env = os.environ.copy()
    env["HERCULES_RC"] = "scripts/ipl.rc"
    env.pop("TK5CONS", None)
    env["TK5CRLF"] = "CRLF"

    print(f"Booting TK5 from {mvs_path} ...")
    with open(log_path, "w", encoding="utf-8", errors="replace") as log_fh:
        proc = subprocess.Popen(
            [herc_exe, "-d", "-f", "conf/tk5.cnf"],
            cwd=str(mvs_path),
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            env=env,
        )
        try:
            rc = _run(mvs_path, log_path, proc)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()

    return rc


def _run(mvs_path: Path, log_path: Path, proc: subprocess.Popen) -> int:
    # 1. wait for JES2
    if not _wait_for(log_path, _JES2_READY_PATTERNS, _BOOT_TIMEOUT, label="JES2"):
        print("\nERROR: JES2 did not become active within 180s")
        _tail(log_path, 20)
        return 1
    print("  JES2 active — submitting job ...")

    # give JES2 a moment to fully initialise before accepting cards
    time.sleep(5)

    # start JES2 printers so MSGCLASS=A output gets written to disk
    _mvs_cmd("$S PRINTER1")
    _mvs_cmd("$S PRINTER2")
    time.sleep(2)

    # 2. submit JCL via socket reader
    if not _submit_jcl(_JCL):
        print("ERROR: could not connect to card reader socket (port 3505)")
        return 1
    print(f"  Job {_JOB_NAME} submitted — waiting for completion ...")

    # 3. wait for HASP395 in log
    completion_patterns = [
        f"$HASP395 {_JOB_NAME}",
        f"HASP395 {_JOB_NAME}",
    ]
    if not _wait_for(log_path, completion_patterns, _JOB_TIMEOUT, label=f"HASP395 {_JOB_NAME}"):
        print(f"\nERROR: {_JOB_NAME} did not complete within {_JOB_TIMEOUT}s")
        _tail(log_path, 30)
        return 1

    print(f"\n  Job {_JOB_NAME} ENDED\n")

    # 4. extract step results from hardcopy.log (always available)
    _print_hardcopy_summary(mvs_path, _JOB_NAME)

    # 5. printer spool files (best effort — PRINTER1 may be inactive)
    _print_output(mvs_path)
    return 0


def _mvs_cmd(cmd: str, port: int = _HTTP_PORT) -> bool:
    """Issue an MVS operator command via the Hercules HTTP console."""
    url = f"http://127.0.0.1:{port}/?cmd={urllib.parse.quote('/' + cmd)}"
    try:
        with urllib.request.urlopen(url, timeout=5):
            return True
    except Exception:
        return False


def _submit_jcl(jcl: str, host: str = "127.0.0.1", port: int = _READER_PORT) -> bool:
    """Send JCL to the TK5 socket card reader (000C)."""
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            s.sendall(jcl.encode("ascii"))
        return True
    except (OSError, ConnectionRefusedError):
        return False


def _wait_for(log_path: Path, patterns: list[str], timeout: int, label: str) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(3)
        if log_path.exists():
            try:
                text = log_path.read_text(errors="replace")
                if any(p in text for p in patterns):
                    return True
            except OSError:
                pass
        sys.stdout.write(".")
        sys.stdout.flush()
    print()
    return False


def _print_hardcopy_summary(mvs_path: Path, job_name: str) -> None:
    """Print IEFACTRT step summary from hardcopy.log."""
    hc = mvs_path / "log" / "hardcopy.log"
    if not hc.exists():
        return
    try:
        lines = hc.read_text(errors="replace").splitlines()
    except OSError:
        return
    in_block = False
    printed = 0
    for line in lines:
        if job_name in line and ("IEFACTRT" in line or "HASP395" in line or "HASP373" in line):
            in_block = True
        if in_block:
            print(" ", line)
            printed += 1
            if printed > 20:
                break


def _print_output(mvs_path: Path) -> None:
    """Print all non-empty printer spool files."""
    prt_dir = mvs_path / "prt"
    if not prt_dir.exists():
        print("(no prt/ directory)")
        return
    printed_any = False
    for prt in sorted(prt_dir.glob("*.txt")):
        try:
            text = prt.read_text(errors="replace").strip()
            if text:
                print(f"=== {prt.name} ===")
                print(text)
                printed_any = True
        except OSError:
            pass
    if not printed_any:
        print("(no printer output files found)")


def _tail(log_path: Path, n: int = 20) -> None:
    try:
        lines = log_path.read_text(errors="replace").splitlines()
        print(f"\n--- last {n} lines of hercules log ---")
        for line in lines[-n:]:
            print(" ", line)
    except OSError:
        pass


if __name__ == "__main__":
    sys.exit(main())
