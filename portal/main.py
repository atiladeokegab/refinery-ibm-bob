from __future__ import annotations

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from portal.auth import authenticate_dev, create_session_token
from portal.routes.dashboard import router as dashboard_router
from portal.routes.audits import router as audits_router
from portal.routes.certificates import router as certs_router
from portal.routes.run_audit import router as run_audit_router
from portal.routes.sign import router as sign_router
from portal.routes.narrative import router as narrative_router
from portal.routes.chat import router as chat_router
from portal.routes.rag import router as rag_router

app = FastAPI(title="Refinery Governance Portal")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_HERE = Path(__file__).parent

try:
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
except Exception:
    templates = None

app.include_router(dashboard_router)
app.include_router(audits_router)
app.include_router(certs_router)
app.include_router(run_audit_router)
app.include_router(sign_router)
app.include_router(narrative_router)
app.include_router(chat_router)
app.include_router(rag_router)

try:
    app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")
except RuntimeError:
    pass


@app.post("/api/login")
async def login(request: Request):
    from fastapi import HTTPException
    body = await request.json()
    user = authenticate_dev(body.get("username", ""), body.get("password", ""))
    if not user:
        raise HTTPException(401, "Invalid credentials")
    token = create_session_token(user=user["user"], role=user["role"])
    return {"token": token, "user": user["user"], "role": user["role"]}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if templates:
        return templates.TemplateResponse(request, "dashboard.html")
    return HTMLResponse("<h1>Refinery Governance Portal</h1><p>Templates not yet installed.</p>")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if templates:
        return templates.TemplateResponse(request, "login.html")
    return HTMLResponse("<h1>Login</h1>")
