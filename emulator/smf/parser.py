"""SMF binary and IFASMFDP text parser for Z-Optima RL."""

import datetime
import re
import struct

from .records import SMFType30, SMFType72, SMFType74

# ---------------------------------------------------------------------------
# Binary decode helpers
# ---------------------------------------------------------------------------

def _decode_packed_bcd_date(raw: bytes) -> datetime.date:
    """4-byte packed BCD YYYYDDD+ → datetime.date.

    Nibble layout: [Y1 Y2 Y3 Y4 D1 D2 D3 sign]
    """
    nibbles = []
    for b in raw:
        nibbles.append((b >> 4) & 0xF)
        nibbles.append(b & 0xF)
    year = nibbles[0] * 1000 + nibbles[1] * 100 + nibbles[2] * 10 + nibbles[3]
    doy  = nibbles[4] * 100 + nibbles[5] * 10 + nibbles[6]
    try:
        return datetime.date(year, 1, 1) + datetime.timedelta(days=max(doy - 1, 0))
    except (ValueError, OverflowError):
        return datetime.date.today()


def _decode_binary_time(hundredths: int) -> datetime.time:
    """4-byte binary time in 1/100-second units → datetime.time."""
    cs   = hundredths % 100
    secs = hundredths // 100
    h    = (secs // 3600) % 24
    m    = (secs % 3600) // 60
    s    = secs % 60
    return datetime.time(h, m, s, microsecond=cs * 10_000)


def _decode_ebcdic(raw: bytes) -> str:
    """Decode EBCDIC bytes (code page 037) and strip padding."""
    try:
        return raw.decode("cp037").strip()
    except Exception:
        return raw.decode("latin-1", errors="replace").strip()


# ---------------------------------------------------------------------------
# IFASMFDP text patterns
# ---------------------------------------------------------------------------

# Compact single-line (HERCULES Phase I synthetic output)
# SMF30 JOB=X STEP=Y PGM=Z DATE=2026123 TIME=12304500 CPU=1234 ELAPSED=5678 EXCP=42 MIPS=1000 RC=0
_COMPACT_RE = re.compile(
    r"SMF30\s+"
    r"JOB=(?P<job>\S+)\s+"
    r"STEP=(?P<step>\S+)\s+"
    r"PGM=(?P<pgm>\S+)\s+"
    r"DATE=(?P<date>\d{7})\s+"
    r"TIME=(?P<time>\d+)\s+"
    r"CPU=(?P<cpu>\d+)\s+"
    r"ELAPSED=(?P<elapsed>\d+)\s+"
    r"EXCP=(?P<excp>\d+)\s+"
    r"MIPS=(?P<mips>\d+)\s+"
    r"RC=(?P<rc>\d+)",
    re.IGNORECASE,
)

# Formatted multi-line IFASMFDP report block
_BLOCK_START_RE = re.compile(r"SMF\s+TYPE\s+30", re.IGNORECASE)
_KV_RE = re.compile(
    r"(?P<key>JOB\s*NAME|STEP\s*NAME|PROGRAM\s*NAME|DATE|TIME|"
    r"CPU\s*TIME|ELAPSED\s*TIME|EXCP\s*COUNT|MIPS|RETURN\s*CODE)"
    r"[\s.:]+(?P<val>\S+)",
    re.IGNORECASE,
)
_JULDATE_RE = re.compile(r"(\d{4})[/.-]?(\d{3})")
_HHMMSS_RE  = re.compile(r"(\d{2}):(\d{2}):(\d{2})")

# IEF376I JOB-level timing from MVS JOBLOG (available when MSGCLASS=A)
# IEF376I  JOB /ZOPTJOB/ STOP  26129.1746 CPU    0MIN 00.34SEC SRB ...
_IEF376I_RE = re.compile(
    r"IEF376I\s+JOB\s+/(\w+)\s*/\s+\S+\s+\S+\s+CPU\s+(\d+)MIN\s+([\d.]+)SEC",
    re.IGNORECASE,
)


def _parse_julian(s: str) -> datetime.date | None:
    m = _JULDATE_RE.search(s)
    if not m:
        return None
    year, doy = int(m.group(1)), int(m.group(2))
    try:
        return datetime.date(year, 1, 1) + datetime.timedelta(days=max(doy - 1, 0))
    except (ValueError, OverflowError):
        return None


def _parse_time(s: str) -> datetime.time | None:
    m = _HHMMSS_RE.search(s)
    if m:
        return datetime.time(int(m.group(1)) % 24, int(m.group(2)), int(m.group(3)))
    if s.isdigit():
        return _decode_binary_time(int(s))
    return None


# ---------------------------------------------------------------------------
# SMFParser
# ---------------------------------------------------------------------------

class SMFParser:
    """Decode SMF records from binary VBS data or IFASMFDP printed output."""

    # ---- binary path -------------------------------------------------------

    def parse_binary(self, data: bytes) -> list[SMFType30]:
        """Parse a VBS binary blob; return all Type 30 step-termination records."""
        records: list[SMFType30] = []
        offset = 0
        while offset + 4 <= len(data):
            rec_len = struct.unpack_from(">H", data, offset)[0]
            if rec_len < 4 or offset + rec_len > len(data):
                break
            rec = data[offset : offset + rec_len]
            if len(rec) >= 3 and rec[2] == 0x1E:
                r = self._decode_type30_binary(rec)
                if r is not None:
                    records.append(r)
            offset += rec_len
        return records

    def _decode_type30_binary(self, rec: bytes) -> SMFType30 | None:
        """Decode one Type 30 binary record per the layout in the task spec."""
        MIN_LEN = 52
        if len(rec) < MIN_LEN:
            return None
        try:
            date     = _decode_packed_bcd_date(rec[4:8])
            time_raw = struct.unpack_from(">I", rec, 8)[0]
            time     = _decode_binary_time(time_raw)
            job_name   = _decode_ebcdic(rec[12:20])
            step_name  = _decode_ebcdic(rec[20:28])
            pgm_name   = _decode_ebcdic(rec[28:36])
            cpu_us     = struct.unpack_from(">I", rec, 36)[0]
            elapsed_us = struct.unpack_from(">I", rec, 40)[0]
            excp       = struct.unpack_from(">I", rec, 44)[0]
            mips_raw   = struct.unpack_from(">I", rec, 48)[0]
            mips       = float(mips_raw) / 1000.0 if mips_raw != 0 else None
        except struct.error:
            return None
        return SMFType30(
            job_name=job_name or "UNKNOWN",
            step_name=step_name or "UNKNOWN",
            program_name=pgm_name or "UNKNOWN",
            cpu_time_us=cpu_us,
            elapsed_time_us=elapsed_us,
            excp_count=excp,
            mips_estimate=mips,
            return_code=0,
            date=date,
            time=time,
        )

    # ---- text / IFASMFDP path ----------------------------------------------

    def parse_ifasmfdp(self, text: str) -> list[SMFType30]:
        """Parse IFASMFDP formatted text; handles compact and report formats."""
        records: list[SMFType30] = []

        # Try compact single-line format first
        for m in _COMPACT_RE.finditer(text):
            g = m.groupdict()
            date = _parse_julian(g["date"]) or datetime.date.today()
            time = _parse_time(g["time"]) or datetime.time()
            mips_raw = int(g["mips"])
            records.append(SMFType30(
                job_name=g["job"],
                step_name=g["step"],
                program_name=g["pgm"],
                cpu_time_us=int(g["cpu"]),
                elapsed_time_us=int(g["elapsed"]),
                excp_count=int(g["excp"]),
                mips_estimate=float(mips_raw) / 1000.0 if mips_raw else None,
                return_code=int(g["rc"]),
                date=date,
                time=time,
            ))

        if records:
            return records

        # Try formatted multi-line report
        return self._parse_report_blocks(text)

    def _parse_report_blocks(self, text: str) -> list[SMFType30]:
        """Extract Type 30 records from formatted IFASMFDP report sections."""
        records: list[SMFType30] = []
        lines = text.splitlines()
        in_block = False
        block_lines: list[str] = []

        for line in lines:
            if _BLOCK_START_RE.search(line):
                if in_block and block_lines:
                    r = self._parse_one_block(block_lines)
                    if r:
                        records.append(r)
                in_block = True
                block_lines = [line]
            elif in_block:
                block_lines.append(line)

        if in_block and block_lines:
            r = self._parse_one_block(block_lines)
            if r:
                records.append(r)

        return records

    def parse_ief376i(self, text: str, job_name: str | None = None) -> int:
        """Return job-total CPU microseconds from the LAST matching IEF376I line.

        prt00e.txt accumulates output from all jobs in the session; taking the
        last matching entry gives the most-recent job's CPU time rather than
        the historical maximum, which would corrupt sequential measurements.

        job_name filters to a specific job (e.g. "ZOPTJOB").
        Returns 0 when no matching line is found.
        """
        last = 0
        for m in _IEF376I_RE.finditer(text):
            if job_name and m.group(1).upper() != job_name.upper():
                continue
            last = int((int(m.group(2)) * 60 + float(m.group(3))) * 1_000_000)
        return last

    def _parse_one_block(self, lines: list[str]) -> SMFType30 | None:
        fields: dict[str, str] = {}
        for line in lines:
            for m in _KV_RE.finditer(line):
                key = re.sub(r"\s+", "_", m.group("key").strip().upper())
                fields[key] = m.group("val").strip()

        job  = fields.get("JOB_NAME", "UNKNOWN")
        step = fields.get("STEP_NAME", "UNKNOWN")
        pgm  = fields.get("PROGRAM_NAME", "UNKNOWN")

        date = _parse_julian(fields.get("DATE", "")) or datetime.date.today()
        time = _parse_time(fields.get("TIME", "")) or datetime.time()

        def _int(key: str) -> int:
            try:
                return int(re.sub(r"[^\d]", "", fields.get(key, "0")) or "0")
            except ValueError:
                return 0

        cpu_us     = _int("CPU_TIME")
        elapsed_us = _int("ELAPSED_TIME")
        excp       = _int("EXCP_COUNT")
        rc         = _int("RETURN_CODE")

        mips_str  = fields.get("MIPS", "0")
        try:
            mips_val: float | None = float(mips_str)
            if mips_val == 0.0:
                mips_val = None
        except ValueError:
            mips_val = None

        if job == "UNKNOWN" and step == "UNKNOWN":
            return None

        return SMFType30(
            job_name=job,
            step_name=step,
            program_name=pgm,
            cpu_time_us=cpu_us,
            elapsed_time_us=elapsed_us,
            excp_count=excp,
            mips_estimate=mips_val,
            return_code=rc,
            date=date,
            time=time,
        )
