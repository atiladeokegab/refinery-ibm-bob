from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from portal.auth import _db_path, verify_session_token
from portal.db import get_record_by_ref_id, update_bob_headline

router = APIRouter()


def _require_token(token: str = Query(...)) -> dict:
    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    return payload


@router.get("/api/audits/{ref_id}/stream-narrative")
def stream_narrative(
    ref_id: str,
    auth: dict = Depends(_require_token),
    db: Path = Depends(_db_path),
):
    record = get_record_by_ref_id(ref_id, db_path=db)
    if not record:
        raise HTTPException(404, f"No record found for ref_id: {ref_id}")

    provider_name = os.environ.get("BOB_PROVIDER", "ibm_bob")

    def _generate():
        try:
            from bob.narrator import _TEMPLATE, _get_provider
            from portal.db import get_record_by_ref_id as _get

            # Build a minimal prompt from the record
            prompt = _TEMPLATE.format(
                verdict=record.verdict,
                risk_score=record.risk_score,
                reduction_pct=record.reduction_pct,
                semantic_changes=json.dumps([]),
                context="{context}",
            )

            provider = _get_provider(provider_name)
            if hasattr(provider, "stream"):
                full = ""
                for token in provider.stream(prompt):
                    full += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
                # Send final parsed narrative
                from bob.narrator import _parse
                narrative = _parse(full)
                update_bob_headline(ref_id, narrative.headline, db_path=db)
                yield f"data: {json.dumps({'done': True, 'headline': narrative.headline, 'summary': narrative.executive_summary})}\n\n"
            else:
                # Non-streaming fallback
                result = provider.complete(prompt)
                from bob.narrator import _parse
                narrative = _parse(result)
                yield f"data: {json.dumps({'token': narrative.executive_summary})}\n\n"
                update_bob_headline(ref_id, narrative.headline, db_path=db)
                yield f"data: {json.dumps({'done': True, 'headline': narrative.headline, 'summary': narrative.executive_summary})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
