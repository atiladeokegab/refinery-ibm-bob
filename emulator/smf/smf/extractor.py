"""SMFExtractor — runs IFASMFDP after a HERCULES job and returns SMFType30 records."""

import textwrap

from .parser import SMFParser
from .records import SMFType30

# JCL submitted to MVS to dump the SMF dataset via IFASMFDP (Phase II path).
# DD names must match what IFASMFDP expects internally on MVS 3.8j:
#   DUMPIN  = input SMF dataset
#   DUMPOUT = required DD for binary copy; DUMMY suppresses the copy
#   SYSPRINT = formatted report output routed to PRINTER1 → prt/prt00e.txt
# SWITCH SMF must be issued before submission to close SYS1.MANX.
# USER=IBMUSER bypasses RAKF protection on SYS1.MANX (SPECIAL attribute).
_IFASMFDP_JCL = textwrap.dedent("""\
    //SMFDUMP  JOB (ACCT),'ZOPTIMA SMF',CLASS=A,MSGCLASS=A,MSGLEVEL=(1,1),
    //             USER=HERC01,PASSWORD=CUL8TR
    //STEP01   EXEC PGM=IFASMFDP
    //SYSPRINT DD  SYSOUT=A
    //DUMPIN   DD  DSN=SYS1.MANX,DISP=SHR
    //DUMPOUT  DD  DUMMY
    //SYSIN    DD  *
      INDD(DUMPIN,OPTIONS(DUMP))
      OUTDD(SYSPRINT,TYPE(30))
    /*
""")


class SMFExtractor:
    """Extract SMF Type 30 step-termination records after a HERCULES job run.

    Phase I (HERCULES only): parses SMF data from the runner's raw output.
    Phase II (full MVS + JCL bridge): submits IFASMFDP JCL via ``jcl_bridge``
    and parses the formatted report.

    Args:
        hercules_runner: HerculesRunner instance (used in Phase I).
        jcl_bridge: Optional JCL bridge (Hermes emulator/bridge/). When
            provided, Phase II IFASMFDP path is used instead of raw output.
    """

    def __init__(self, hercules_runner, jcl_bridge=None):
        self._runner = hercules_runner
        self._bridge = jcl_bridge
        self._parser = SMFParser()

    def extract(self, raw_output: str) -> list[SMFType30]:
        """Return SMFType30 records from a completed job run.

        Args:
            raw_output: stdout+stderr captured from HerculesRunner after the job.

        Returns:
            List of SMFType30 records (may be empty if HERCULES did not emit
            SMF data, which is normal in Phase I emulator mode).
        """
        if self._bridge is not None:
            return self._extract_via_ifasmfdp()
        return self._extract_from_raw(raw_output)

    def extract_to_state_dict(self, raw_output: str) -> dict:
        """Convenience wrapper — return the first record as a dict keyed to
        SMFStateVector fields, with safe defaults when no record is found.
        """
        records = self.extract(raw_output)
        if not records:
            return {
                "cpu_time_us": 0,
                "elapsed_time_us": 0,
                "excp_count": 0,
                "mips_estimate": 0.0,
                "return_code": 0,
            }
        r = records[0]
        return {
            "cpu_time_us": r.cpu_time_us,
            "elapsed_time_us": r.elapsed_time_us,
            "excp_count": r.excp_count,
            "mips_estimate": r.mips_estimate if r.mips_estimate is not None else 0.0,
            "return_code": r.return_code,
        }

    def parse_ief376i(self, prt_text: str, job_name: str | None = None) -> int:
        """Extract job-total CPU microseconds from IEF376I lines in JOBLOG."""
        return self._parser.parse_ief376i(prt_text, job_name)

    # ---- private -----------------------------------------------------------

    def _extract_from_raw(self, raw_output: str) -> list[SMFType30]:
        """Phase I: parse SMF lines embedded in HERCULES console output."""
        return self._parser.parse_ifasmfdp(raw_output)

    def _extract_via_ifasmfdp(self) -> list[SMFType30]:
        """Phase II: submit IFASMFDP JCL and parse the formatted report."""
        import sys
        try:
            output = self._bridge.submit_jcl(_IFASMFDP_JCL)
        except Exception as exc:
            print(f"[SMFExtractor] Phase II submit failed: {exc}", file=sys.stderr)
            return []
        if not output:
            print("[SMFExtractor] Phase II: no output from IFASMFDP", file=sys.stderr)
            return []
        records = self._parser.parse_ifasmfdp(output)
        print(f"[SMFExtractor] Phase II: parsed {len(records)} record(s)", file=sys.stderr)
        if not records:
            print(f"[SMFExtractor] Phase II raw output (first 500 chars):\n{output[:500]}", file=sys.stderr)
        return records
