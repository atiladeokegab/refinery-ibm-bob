from __future__ import annotations

import argparse
from pathlib import Path

from audit.engine import run_audit
from audit.report import generate_pdf


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m audit",
        description="Refinery IV&V — independent verification of AI-modified COBOL",
    )
    parser.add_argument("original", type=Path, help="Original COBOL source file")
    parser.add_argument("modified", type=Path, help="AI-modified COBOL source file")
    parser.add_argument("--output", type=Path, default=Path("report.pdf"),
                        help="Output PDF path (default: report.pdf)")
    parser.add_argument("--ref-id", default="", metavar="ID",
                        help="Audit reference ID (auto-generated if omitted)")
    parser.add_argument("--client-ref", default="", metavar="REF",
                        help="Client reference string")
    args = parser.parse_args()

    result = run_audit(
        args.original,
        args.modified,
        ref_id=args.ref_id,
        client_ref=args.client_ref,
    )
    generate_pdf(result, args.output)

    d = result.diff
    print(f"Verdict      : {d.verdict}")
    print(f"Reference    : {result.ref_id}")
    print(f"Original     : {result.original_file}")
    print(f"Modified     : {result.modified_file}")
    print(f"CPU reduction: {d.reduction_pct}%")
    print(f"Divergences  : {len(d.semantic_changes)}")
    print(f"Report       : {args.output}")
