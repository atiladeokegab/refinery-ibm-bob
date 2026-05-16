from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from fastapi import APIRouter, Depends, Query
from portal.auth import _require_auth, _db_path
from portal.db import get_records

router = APIRouter()


@router.get("/api/audits")
def list_audits(
    auth: dict = Depends(_require_auth),
    verdict: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Path = Depends(_db_path),
):
    records = get_records(db_path=db, verdict=verdict, limit=limit, offset=offset)
    return [asdict(r) for r in records]
