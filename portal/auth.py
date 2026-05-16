from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

_SECRET = os.environ.get("PORTAL_SECRET", "dev-secret-change-in-production")

_DEV_USERS: dict[str, dict] = {
    "admin": {"password": os.environ.get("PORTAL_ADMIN_PASSWORD", "refinery"), "role": "admin"},
}


def _sign(data: str) -> str:
    return hmac.new(_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()


def create_session_token(user: str, role: str) -> str:
    payload = json.dumps({"user": user, "role": role, "exp": int(time.time()) + 86400})
    sig = _sign(payload)
    encoded = base64.urlsafe_b64encode(payload.encode()).decode()
    return f"{encoded}.{sig}"


def verify_session_token(token: str) -> dict[str, Any] | None:
    try:
        encoded, sig = token.rsplit(".", 1)
        payload_str = base64.urlsafe_b64decode(encoded.encode()).decode()
        if not hmac.compare_digest(_sign(payload_str), sig):
            return None
        payload = json.loads(payload_str)
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def authenticate_dev(username: str, password: str) -> dict | None:
    """Dev-mode authentication. Replace with LDAP in production."""
    user = _DEV_USERS.get(username)
    if user and user["password"] == password:
        return {"user": username, "role": user["role"]}
    return None


# FastAPI dependency utilities for portal routes
from pathlib import Path as _Path
from fastapi import Depends, Header, HTTPException


def _db_path() -> _Path:
    return _Path(os.environ.get("PORTAL_DB_PATH", "portal.db"))


def _require_auth(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    token = authorization.removeprefix("Bearer ")
    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    return payload
