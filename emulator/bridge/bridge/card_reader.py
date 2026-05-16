"""CardReader — writes JCL to the HERCULES virtual card reader device."""

import re
import uuid
from pathlib import Path


class CardReader:
    """Submits a JCL job by writing it to the HERCULES reader path.

    HERCULES watches the reader_path file; once written, it treats the
    content as a card-image job stream and queues it for execution.
    """

    def submit(self, jcl: str, reader_path: Path) -> str:
        """Write jcl to reader_path and return the job_id (JOB name from JCL)."""
        job_id = self._extract_job_name(jcl)
        reader_path.write_text(jcl, encoding="utf-8")
        return job_id

    def _extract_job_name(self, jcl: str) -> str:
        m = re.match(r"//(\w{1,8})\s+JOB\b", jcl)
        if m:
            return m.group(1)
        return f"JOB{uuid.uuid4().hex[:4].upper()}"
