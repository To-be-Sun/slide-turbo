"""
Slide Turbo — FastAPI エントリーポイント
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import connect_db, disconnect_db
from app.presentation.api import api_router
from app.shared.exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


# ── Lifespan ──────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """起動時に DB 接続、終了時に切断"""
    await connect_db()
    yield
    await disconnect_db()


# ── App ───────────────────────────────────────────────


app = FastAPI(
    title="Slide Turbo API",
    version="0.1.0",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ────────────────────────────────


_STATUS_MAP: dict[type, int] = {
    NotFoundException: 404,
    UnauthorizedException: 401,
    ForbiddenException: 403,
    ConflictException: 409,
    ValidationException: 422,
}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    status = _STATUS_MAP.get(type(exc), 500)
    return JSONResponse(status_code=status, content={"detail": exc.detail})


# ── Routers ───────────────────────────────────────────


app.include_router(api_router)


# ── Health Check ──────────────────────────────────────


@app.get("/health")
async def health():
    return {"status": "ok"}
