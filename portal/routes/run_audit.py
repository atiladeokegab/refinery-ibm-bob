from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AuditRunRequest(BaseModel):
    repo_path: str
    changed_file: str
    estate: bool = False


@router.post("/api/audit/run")
def run_audit_endpoint(req: AuditRunRequest):
    repo = Path(req.repo_path)
    if not repo.exists():
        raise HTTPException(400, f"repo_path not found: {repo}")

    git_result = subprocess.run(
        ["git", "show", f"HEAD:{req.changed_file}"],
        cwd=str(repo),
        capture_output=True,
    )
    if git_result.returncode != 0:
        raise HTTPException(
            400,
            f"Could not retrieve original from git HEAD: {git_result.stderr.decode()[:200]}",
        )

    modified_path = repo / req.changed_file
    if not modified_path.exists():
        raise HTTPException(400, f"changed_file not found: {modified_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        stem = Path(req.changed_file).stem
        original = tmp / f"{stem}.cob"
        modified = tmp / f"{stem}_modified.cob"
        original.write_bytes(git_result.stdout)
        modified.write_bytes(modified_path.read_bytes())

        from audit.engine import run_audit
        estate_root = repo if req.estate else None
        audit = run_audit(original, modified, estate_root=estate_root)

        # Self-correction loop: if Bob's edit was FLAGGED, ask Bob to fix it
        correction_count = 0
        if audit.diff.verdict == "FLAGGED":
            try:
                from bob.corrector import correct
                from bob.rag.ingester import ingest_failure
                cr = correct(original, modified, audit)
                correction_count = cr.correction_count
                if cr.correction_count > 0:
                    audit = cr.final_audit
                ingest_failure(
                    program=stem,
                    semantic_changes=audit.diff.semantic_changes,
                    signal_type="semantic_failure",
                )
            except Exception:
                pass  # correction failure must never block the audit record

        narrative = None
        try:
            from bob.narrator import narrate
            narrative = narrate(audit)
        except Exception:
            pass

        from audit.report import generate_pdf
        contracts_dir = repo / "refinery" / "audits" / audit.ref_id / "report"
        contracts_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(req.changed_file).stem
        pdf_path = contracts_dir / f"CHANGE-CONTRACT-{stem}-{audit.date}.pdf"
        sha256 = generate_pdf(audit, pdf_path, narrative)

        try:
            from portal.db import write_audit_record
            write_audit_record(
                audit,
                pdf_path=pdf_path,
                sha256=sha256,
                bob_headline=narrative.headline if narrative else None,
                correction_count=correction_count,
            )
        except Exception:
            pass

        impact = getattr(audit, "impact", None)
        return {
            "ref_id": audit.ref_id,
            "verdict": audit.diff.verdict,
            "risk_score": audit.diff.risk_score,
            "blast_radius_score": impact.blast_radius_score if impact else 0,
            "affected_systems_count": len(impact.affected_systems) if impact else 0,
            "affected_systems": impact.affected_systems if impact else [],
            "checks_run": audit.diff.checks_run,
            "pdf_ref_id": audit.ref_id,
            "correction_count": correction_count,
        }
