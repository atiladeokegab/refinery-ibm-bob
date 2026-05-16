"""JCLBridge — submits JCL to live TK5, waits for completion, returns printer output.

Used by SMFExtractor Phase II to submit IFASMFDP dump jobs and retrieve their
SYSPRINT output from the JES2 printer spool file.
"""
from __future__ import annotations

import re
import socket
import time
import urllib.parse
import urllib.request
from pathlib import Path

_READER_PORT  = 3505   # TK5 socket card reader (device 000C)
_HTTP_PORT    = 8038   # TK5 Hercules HTTP console
_JOB_TIMEOUT  = 120    # seconds to wait for job completion


class JCLBridge:
    """Submit JCL to a live TK5 instance and return printed SYSPRINT output.

    Uses the socket card reader (port 3505) for submission — the same path
    confirmed working in live_job_test.py.  Printer output is read from
    prt/prt00e.txt after activating PRINTER1 via the Hercules HTTP console.

    Args:
        mvs_path:  Root of the TK5 installation (must contain log/, prt/).
        http_port: Hercules HTTP API port (default 8038).
    """

    def __init__(self, mvs_path: Path, http_port: int = _HTTP_PORT) -> None:
        self._mvs_path  = Path(mvs_path)
        self._http_port = http_port
        self._prt_path  = self._mvs_path / "prt" / "prt00e.txt"
        self._log_path  = self._mvs_path / "log" / "3033.log"

    def submit_jcl(self, jcl: str) -> str:
        """Submit JCL, wait for completion, return printer output text.

        Returns empty string on timeout or if the printer file is unavailable.
        """
        import sys
        job_name = self._extract_job_name(jcl)
        print(f"[JCLBridge] submitting {job_name!r}", file=sys.stderr)

        # IFA006A is a WTOR asking operator to confirm dumping the active SMF
        # dataset.  Set up a HAO rule to auto-reply U (proceed) before submitting,
        # then delete it after.  The reply ID is captured via regex group 'rtc'.
        self._herc_cmd(r"hao tgt (?P<rtc>\d+) IFA006A")
        self._herc_cmd(r"hao cmd /r %(rtc)s,u")

        # Switch SMF recording to the alternate dataset so DUMPIN (SYS1.MANX)
        # is closed and IFASMFDP can open it with DISP=SHR.
        self._mvs_cmd("SWITCH SMF")
        time.sleep(5)  # allow SMF switch to complete before IFASMFDP opens DUMPIN

        # Stop any stale warm-start printer entry, then restart fresh.
        # $P stops if running; $S starts — both are no-ops if state already matches.
        self._mvs_cmd("$P PRINTER1")
        time.sleep(1)
        ok = self._mvs_cmd("$S PRINTER1")
        print(f"[JCLBridge] $S PRINTER1 -> {ok}", file=sys.stderr)
        time.sleep(2)

        # Mark start position in log so we only match THIS job's HASP395
        log_start = self._log_size()

        # Clear stale printer output and submit
        self._clear_prt()
        if not self._submit_socket(jcl):
            return ""

        # Wait for $HASP395 <JOBNAME> ENDED
        if not self._wait_hasp395(job_name, log_start):
            return ""

        # Remove the IFA006A auto-reply rule now that the job has completed.
        self._herc_cmd("hao del IFA006A")

        # Wait for JES2 to print SYSOUT datasets to disk.  JES2 first flushes
        # the JOBLOG (MSGLEVEL output), then the job-end separator, then each
        # SYSOUT class-A dataset.  Poll until the file size stops growing.
        prev_size = -1
        for _ in range(15):          # at most 30 seconds
            time.sleep(2)
            try:
                cur_size = self._prt_path.stat().st_size
            except OSError:
                cur_size = 0
            if cur_size == prev_size and cur_size > 0:
                break
            prev_size = cur_size

        output = self._read_prt()
        print(f"[JCLBridge] prt00e.txt length={len(output)}", file=sys.stderr)
        return output

    def setup_printer(self) -> None:
        """Stop/restart PRINTER1 and clear prt00e.txt for a fresh job run."""
        self._mvs_cmd("$P PRINTER1")
        time.sleep(1)
        self._clear_prt()
        self._mvs_cmd("$S PRINTER1")
        time.sleep(2)

    def wait_for_print(self, max_wait: int = 30) -> str:
        """Poll prt00e.txt until file size stabilizes; return content."""
        prev_size = -1
        for _ in range(max_wait // 2):
            time.sleep(2)
            try:
                cur_size = self._prt_path.stat().st_size
            except OSError:
                cur_size = 0
            if cur_size == prev_size and cur_size > 0:
                break
            prev_size = cur_size
        return self._read_prt()

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_job_name(jcl: str) -> str:
        m = re.match(r"//(\w{1,8})\s+JOB\b", jcl)
        return m.group(1) if m else "SMFDUMP"

    def _mvs_cmd(self, cmd: str) -> bool:
        """Send an MVS operator command via the Hercules HTTP console.

        Hercules 4.x uses POST /cgi-bin/tasks/syslog with command= field.
        The leading '/' routes the command to MVS.
        """
        data = urllib.parse.urlencode({"command": "/" + cmd}).encode("ascii")
        url  = f"http://127.0.0.1:{self._http_port}/cgi-bin/tasks/syslog"
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=5):
                return True
        except Exception as exc:
            import sys
            print(f"[JCLBridge] _mvs_cmd({cmd!r}) failed: {exc}", file=sys.stderr)
            return False

    def _herc_cmd(self, cmd: str) -> bool:
        """Send a Hercules console command (no MVS routing — no leading /)."""
        data = urllib.parse.urlencode({"command": cmd}).encode("ascii")
        url  = f"http://127.0.0.1:{self._http_port}/cgi-bin/tasks/syslog"
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=5):
                return True
        except Exception as exc:
            import sys
            print(f"[JCLBridge] _herc_cmd({cmd!r}) failed: {exc}", file=sys.stderr)
            return False

    def _submit_socket(self, jcl: str) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", _READER_PORT), timeout=10) as s:
                s.sendall(jcl.encode("ascii"))
            return True
        except OSError as exc:
            import sys
            print(f"[JCLBridge] socket submit failed: {exc}", file=sys.stderr)
            return False

    def _log_size(self) -> int:
        try:
            return self._log_path.stat().st_size
        except OSError:
            return 0

    def _wait_hasp395(self, job_name: str, log_start: int) -> bool:
        import sys
        ok_pattern   = f"$HASP395 {job_name}"
        term_pattern = f"$HASP396 {job_name}"
        deadline = time.monotonic() + _JOB_TIMEOUT
        while time.monotonic() < deadline:
            time.sleep(2)
            try:
                tail = self._log_path.read_bytes()[log_start:].decode(
                    "utf-8", errors="replace"
                )
                if ok_pattern in tail:
                    return True
                if term_pattern in tail:
                    print(f"[JCLBridge] job terminated early ({term_pattern!r})", file=sys.stderr)
                    return False
            except OSError:
                pass
        print(f"[JCLBridge] timeout waiting for {ok_pattern!r}", file=sys.stderr)
        return False

    def _clear_prt(self) -> None:
        try:
            self._prt_path.write_text("", encoding="utf-8")
        except OSError:
            pass

    def _read_prt(self) -> str:
        try:
            return self._prt_path.read_text(errors="replace")
        except OSError:
            return ""
