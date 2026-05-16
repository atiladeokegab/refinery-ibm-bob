from __future__ import annotations

import importlib.metadata
import random
import string
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from audit.differ import DiffResult, run_diff

if TYPE_CHECKING:
    from estate.impact import ImpactResult


@dataclass
class AuditResult:
    ref_id: str
    date: str
    client_ref: str
    original_file: str
    modified_file: str
    diff: DiffResult
    refinery_version: str
    runner_type: str = "SyntheticRunner"
    impact: "ImpactResult | None" = field(default=None, compare=False)


def _gen_ref_id() -> str:
    suffix = "".join(random.choices(string.digits, k=4))
    return f"REF-{date.today().strftime('%Y%m%d')}-{suffix}"


def _version() -> str:
    try:
        return importlib.metadata.version("z-optima-rl")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"


def run_audit(
    original_path: Path,
    modified_path: Path,
    ref_id: str = "",
    client_ref: str = "",
    write_portal_record: bool = False,
    pdf_path: Path | None = None,
    sha256: str | None = None,
    bob_headline: str | None = None,
    estate_root: Path | None = None,
) -> AuditResult:
    if not ref_id:
        ref_id = _gen_ref_id()
    diff = run_diff(original_path, modified_path, repo_root=Path(estate_root) if estate_root else None)
    result = AuditResult(
        ref_id=ref_id,
        date=date.today().isoformat(),
        client_ref=client_ref,
        original_file=Path(original_path).name,
        modified_file=Path(modified_path).name,
        diff=diff,
        refinery_version=_version(),
        runner_type=diff.runner_type,
    )
    if estate_root is not None:
        try:
            from estate.graph import build_graph_from_root
            from estate.impact import compute_impact
            program_name = Path(original_path).stem.upper()
            graph = build_graph_from_root(Path(estate_root))
            result.impact = compute_impact(program_name, graph)
        except Exception:
            pass  # estate analysis is optional — never fail the audit
    if write_portal_record:
        try:
            from portal.db import write_audit_record as _write
            _write(result, pdf_path=pdf_path, sha256=sha256, bob_headline=bob_headline)
        except Exception:
            pass  # portal DB is optional — never fail the audit
    return result
