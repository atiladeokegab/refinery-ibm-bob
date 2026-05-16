"""RemoteHerculesPool - same acquire()/release() interface as HerculesPool
but backed by HTTP calls to pool_server.py.

Auto-selection helper:
    from emulator.remote_pool import make_pool
    pool = make_pool(n=4, base_conf=..., base_dasd=...)
    # Returns RemoteHerculesPool if CLOUD_POOL_URL is set, else HerculesPool.

Usage:
    with RemoteHerculesPool("http://pool-server:9000") as pool:
        slot = pool.acquire()
        try:
            # slot.card_reader_path, slot.http_port, slot.cnsl_port available
            ...
        finally:
            pool.release(slot)
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import httpx


_ACQUIRE_TIMEOUT_S = 120  # total wait for a free slot
_RETRY_INTERVAL_S = 1.0   # sleep between acquire retries
_HTTP_TIMEOUT_S = 10      # per-request httpx timeout


@dataclass
class RemoteSlot:
    """Mirrors the caller-visible attributes of PoolSlot for remote slots."""

    slot_id:          int
    workdir:          str        # remote path - informational only
    card_reader_path: str        # remote path - informational only
    http_port:        int
    cnsl_port:        int
    _lease_token:     str        # opaque token returned by /slot/acquire

    @property
    def dasd_path(self) -> str:
        """Compatibility shim - remote slots have no local DASD path."""
        return ""


class RemoteHerculesPool:
    """Thread-safe pool client that delegates to a remote pool_server.py.

    Parameters
    ----------
    base_url:
        Base URL of the pool server, e.g. "http://pool-server:9000".
        Must NOT have a trailing slash.
    acquire_timeout:
        Total seconds to wait for a free slot before raising RuntimeError.
    """

    def __init__(
        self,
        base_url: str,
        acquire_timeout: float = _ACQUIRE_TIMEOUT_S,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._acquire_timeout = acquire_timeout
        self._client: httpx.Client | None = None

    # -- Context manager -------------------------------------------------------

    def __enter__(self) -> "RemoteHerculesPool":
        self._client = httpx.Client(timeout=_HTTP_TIMEOUT_S)
        self._check_health()
        return self

    def __exit__(self, *_) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # -- Public API ------------------------------------------------------------

    def acquire(self) -> RemoteSlot:
        """Block until a free slot is available; return a RemoteSlot.

        Retries POST /slot/acquire every _RETRY_INTERVAL_S seconds.
        Raises RuntimeError if no slot is available within acquire_timeout.
        """
        deadline = time.monotonic() + self._acquire_timeout
        while True:
            slot = self._try_acquire()
            if slot is not None:
                return slot
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    f"RemoteHerculesPool: no free slot after {self._acquire_timeout}s "
                    f"(server: {self._base_url})"
                )
            time.sleep(_RETRY_INTERVAL_S)

    def release(self, slot: RemoteSlot) -> None:
        """Release the slot back to the server pool.

        POST /slot/release with the lease token obtained during acquire().
        A 404 response (already freed) is logged but does not raise.
        """
        client = self._ensure_client()
        try:
            resp = client.post(
                f"{self._base_url}/slot/release",
                json={"lease_token": slot._lease_token},
            )
            if resp.status_code == 404:
                import warnings
                warnings.warn(
                    f"RemoteHerculesPool.release: server returned 404 for token "
                    f"{slot._lease_token!r}; slot may have already been freed.",
                    stacklevel=2,
                )
            else:
                resp.raise_for_status()
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"RemoteHerculesPool: network error on release: {exc}"
            ) from exc

    # -- Private helpers -------------------------------------------------------

    def _try_acquire(self) -> RemoteSlot | None:
        """Issue one POST /slot/acquire; return RemoteSlot on 200, None on 503."""
        client = self._ensure_client()
        try:
            resp = client.post(f"{self._base_url}/slot/acquire")
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"RemoteHerculesPool: network error on acquire: {exc}"
            ) from exc

        if resp.status_code == 503:
            return None
        resp.raise_for_status()

        data = resp.json()
        return RemoteSlot(
            slot_id=data["slot_id"],
            workdir=data["workdir"],
            card_reader_path=data["card_reader_path"],
            http_port=data["http_port"],
            cnsl_port=data["cnsl_port"],
            _lease_token=data["lease_token"],
        )

    def _check_health(self) -> None:
        """Raise RuntimeError if the pool server is not healthy."""
        client = self._ensure_client()
        try:
            resp = client.get(f"{self._base_url}/health")
            resp.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            raise RuntimeError(
                f"RemoteHerculesPool: health check failed for {self._base_url}: {exc}"
            ) from exc

    def _ensure_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=_HTTP_TIMEOUT_S)
        return self._client


# -- Auto-selection factory ---------------------------------------------------

def make_pool(
    n: int,
    base_conf: Path,
    base_dasd: Path,
    acquire_timeout: float = _ACQUIRE_TIMEOUT_S,
) -> Union["RemoteHerculesPool", "HerculesPool"]:  # noqa: F821 - lazy import
    """Return RemoteHerculesPool if CLOUD_POOL_URL is set, else HerculesPool.

    Drop-in replacement for direct HerculesPool instantiation:

        pool = make_pool(n=4, base_conf=Path(...), base_dasd=Path(...))
        with pool:
            slot = pool.acquire()
            ...
    """
    url = os.environ.get("CLOUD_POOL_URL")
    if url:
        return RemoteHerculesPool(url, acquire_timeout=acquire_timeout)

    from emulator.pool import HerculesPool
    return HerculesPool(n=n, base_conf=base_conf, base_dasd=base_dasd)
