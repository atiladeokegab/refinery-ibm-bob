from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse
from portal.auth import _require_auth, _db_path, verify_session_token
from portal.db import get_records

router = APIRouter()


def _token_auth(
    authorization: str = Header(default=""),
    token: str = Query(default=""),
) -> dict:
    """Accept token from Authorization header or ?token= query param (for window.open downloads)."""
    raw = token or authorization.removeprefix("Bearer ")
    payload = verify_session_token(raw)
    if not payload:
        raise HTTPException(401, "Missing or invalid token")
    return payload


@router.get("/api/certificates/{ref_id}")
def get_certificate(ref_id: str, auth: dict = Depends(_token_auth), db: Path = Depends(_db_path)):
    records = get_records(db)
    match = next((r for r in records if r.ref_id == ref_id), None)
    if not match:
        raise HTTPException(404, f"No audit record found for {ref_id}")
    if not match.pdf_path or not Path(match.pdf_path).exists():
        raise HTTPException(404, "PDF not available for this audit")
    return FileResponse(match.pdf_path, media_type="application/pdf",
                        headers={"Content-Disposition": "inline"})
