"""pool_server.py - FastAPI server that wraps a local HerculesPool and
exposes it over HTTP for RemoteHerculesPool clients.

Endpoints:
    POST /slot/acquire   -- acquire a pool slot; returns lease token + slot info
    POST /slot/release   -- release a slot by lease token
    GET  /health         -- liveness + free-slot count

Environment variables:
    POOL_SIZE   (int, default 4)       -- number of Hercules slots to start
    BASE_CONF   (str, required)        -- path to hercules_template.conf
    BASE_DASD   (str, required)        -- path to scratch_base DASD image
    SERVER_PORT (int, default 9000)    -- uvicorn listen port

Run:
    uvicorn emulator.pool_server:app --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

import os
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from emulator.pool import HerculesPool, PoolSlot


# -- Globals (initialised in lifespan) ----------------------------------------

_pool: Optional[HerculesPool] = None
_leases: dict[str, PoolSlot] = {}   # lease_token -> PoolSlot
_leases_lock = threading.Lock()


# -- Lifespan -----------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _pool

    pool_size = int(os.environ.get("POOL_SIZE", "4"))
    base_conf = Path(os.environ.get("BASE_CONF", "emulator/config/hercules_template.conf"))
    base_dasd = Path(os.environ.get("BASE_DASD", ""))

    _pool = HerculesPool(n=pool_size, base_conf=base_conf, base_dasd=base_dasd)
    _pool.__enter__()

    yield

    _pool.__exit__(None, None, None)
    _pool = None


# -- App ----------------------------------------------------------------------

app = FastAPI(title="HerculesPool Server", lifespan=lifespan)


# -- Request / response models ------------------------------------------------

class AcquireResponse(BaseModel):
    slot_id:          int
    workdir:          str
    card_reader_path: str
    http_port:        int
    cnsl_port:        int
    lease_token:      str


class ReleaseRequest(BaseModel):
    lease_token: str


class ReleaseResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    slots_total: int
    slots_free: int


# -- Routes -------------------------------------------------------------------

@app.post("/slot/acquire", response_model=AcquireResponse)
def acquire_slot():
    """Acquire a free pool slot.

    Non-blocking semaphore check: returns 503 immediately if no slot is free.
    RemoteHerculesPool handles the retry loop on the client side.
    """
    if _pool is None:
        raise HTTPException(status_code=503, detail="pool not initialised")

    acquired = _pool._sem.acquire(blocking=False)
    if not acquired:
        raise HTTPException(status_code=503, detail="pool exhausted")

    with _pool._lock:
        slot = _pool._free.pop()

    lease_token = secrets.token_hex(16)
    with _leases_lock:
        _leases[lease_token] = slot

    return AcquireResponse(
        slot_id=slot.slot_id,
        workdir=str(slot.workdir),
        card_reader_path=str(slot.card_reader_path),
        http_port=slot.http_port,
        cnsl_port=slot.cnsl_port,
        lease_token=lease_token,
    )


@app.post("/slot/release", response_model=ReleaseResponse)
def release_slot(body: ReleaseRequest):
    """Release a slot identified by its lease token.

    Returns 404 if the token is unknown (e.g. already released).
    """
    if _pool is None:
        raise HTTPException(status_code=503, detail="pool not initialised")

    with _leases_lock:
        slot = _leases.pop(body.lease_token, None)

    if slot is None:
        raise HTTPException(status_code=404, detail="unknown token")

    _pool.release(slot)
    return ReleaseResponse(status="released")


@app.get("/health", response_model=HealthResponse)
def health():
    """Return pool liveness and free-slot count."""
    if _pool is None:
        raise HTTPException(status_code=503, detail="pool not initialised")

    with _pool._lock:
        free_count = len(_pool._free)
        total_count = len(_pool._slots)

    return HealthResponse(
        status="ok",
        slots_total=total_count,
        slots_free=free_count,
    )


# -- Entrypoint (for direct execution) ----------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("SERVER_PORT", "9000"))
    uvicorn.run("emulator.pool_server:app", host="0.0.0.0", port=port, reload=False)
