"""SpoolMonitor — polls HERCULES console log for JES2 job completion."""

import re
import time
from pathlib import Path

# Patterns that signal job end in HERCULES/JES2 console output
_COMPLETION_PATTERNS = [
    r"\$HASP395\s+{job_id}\s+ENDED",   # JES2 normal end
    r"\$HASP395\s+{job_id}\s+PURGED",  # JES2 purged
    r"{job_id}.*\bENDED\b",            # generic fallback
]

_LOG_CANDIDATES = ["hercules.log", "console.log", "jes2.log", "syslog"]


class SpoolMonitor:
    """Polls workdir log files until job_id completion is detected."""

    def __init__(self, poll_interval: float = 0.5):
        self.poll_interval = poll_interval

    def wait(self, job_id: str, workdir: Path, timeout: int = 120) -> int:
        """Block until job_id finishes or timeout expires.

        Returns the job return code (0 = success, >0 = error, -1 = timeout).
        """
        deadline = time.monotonic() + timeout
        patterns = [re.compile(p.format(job_id=re.escape(job_id)), re.IGNORECASE)
                    for p in _COMPLETION_PATTERNS]

        while time.monotonic() < deadline:
            text = self._read_logs(workdir)
            if text:
                for pat in patterns:
                    if pat.search(text):
                        return self._parse_return_code(text, job_id)
            time.sleep(self.poll_interval)

        return -1  # timeout

    def _read_logs(self, workdir: Path) -> str:
        combined = []
        for name in _LOG_CANDIDATES:
            log = workdir / name
            if log.exists():
                try:
                    combined.append(log.read_text(errors="replace"))
                except OSError:
                    pass
        # Also collect any *.log files not in the fixed list
        for log in workdir.glob("*.log"):
            if log.name not in _LOG_CANDIDATES:
                try:
                    combined.append(log.read_text(errors="replace"))
                except OSError:
                    pass
        return "\n".join(combined)

    def _parse_return_code(self, text: str, job_id: str) -> int:
        # $HASP395 JOBNAME ENDED - COND CODE 0000
        m = re.search(
            rf"\$HASP395\s+{re.escape(job_id)}\s+ENDED.*?COND\s+CODE\s+(\d+)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if m:
            return int(m.group(1))
        # Fallback: RC= annotation
        m = re.search(
            rf"{re.escape(job_id)}.*?RC=(\d+)",
            text,
            re.IGNORECASE,
        )
        if m:
            return int(m.group(1))
        return 0
