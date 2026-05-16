from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Depends
from portal.auth import _require_auth, _db_path
from portal.db import get_kpis

router = APIRouter()


@router.get("/api/dashboard")
def dashboard(auth: dict = Depends(_require_auth), db: Path = Depends(_db_path)):
    return get_kpis(db)
