from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic import StringConstraints

from portal.auth import _require_auth, _db_path
from portal.db import sign_contract, get_record_by_ref_id, reject_record

router = APIRouter()

NonBlankStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class SignRequest(BaseModel):
    cro_name: NonBlankStr
    approval_reason: NonBlankStr


class RejectRequest(BaseModel):
    cro_name: NonBlankStr
    rejection_reason: NonBlankStr


@router.post("/api/audits/{ref_id}/sign")
def sign_audit(
    ref_id: str,
    req: SignRequest,
    auth: dict = Depends(_require_auth),
    db: Path = Depends(_db_path),
):
    # Guard: don't allow overwriting a committed signature
    existing = get_record_by_ref_id(ref_id, db_path=db)
    if not existing:
        raise HTTPException(404, f"No record found for ref_id: {ref_id}")
    if existing.signed_at is not None:
        raise HTTPException(409, "Record already signed")

    record = sign_contract(ref_id, req.cro_name, approval_reason=req.approval_reason, db_path=db)
    if not record:
        raise HTTPException(404, f"No record found for ref_id: {ref_id}")
    return {
        "signed": True,
        "ref_id": ref_id,
        "signed_by": record.signed_by,
        "signed_at": record.signed_at,
        "signed_reason": record.signed_reason,
    }


@router.post("/api/audits/{ref_id}/reject")
def reject_audit(
    ref_id: str,
    req: RejectRequest,
    auth: dict = Depends(_require_auth),
    db: Path = Depends(_db_path),
):
    existing = get_record_by_ref_id(ref_id, db_path=db)
    if not existing:
        raise HTTPException(404, f"No record found for ref_id: {ref_id}")
    if existing.signed_at is not None:
        raise HTTPException(409, "Record already signed — cannot reject")
    if existing.rejected_at is not None:
        raise HTTPException(409, "Record already rejected")

    record = reject_record(ref_id, req.cro_name, req.rejection_reason, db_path=db)
    if not record:
        raise HTTPException(404, f"No record found for ref_id: {ref_id}")

    try:
        from bob.rag.ingester import ingest_failure
        ingest_failure(
            program=record.program,
            semantic_changes=[],
            signal_type="cro_rejection",
            reason=req.rejection_reason,
        )
    except Exception:
        pass  # ingestion failure must never block the rejection response

    return {
        "rejected": True,
        "ref_id": ref_id,
        "rejected_by": record.rejected_by,
        "rejected_at": record.rejected_at,
        "rejection_reason": record.rejection_reason,
    }
