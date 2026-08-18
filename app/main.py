from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.rag_routes import router as rag_router
from app.api.routes import router
from app.models.database import Base, SessionLocal, engine
from app.operator_ui import operator_workspace
from app.services.rag_indexer import get_index_stats

# Create all tables on startup (idempotent).
Base.metadata.create_all(bind=engine)

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
GIT_REVISION = os.getenv("GIT_REVISION", "unknown")
APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Guided Agent OS",
    description=(
        "A guided intake and controlled RAG agent platform that validates "
        "required fields, asks clarification questions, normalizes input, "
        "persists runs, and supports a controlled_rag_agent workflow with "
        "local grounded RAG answers, planned-only tool/API plans, and human "
        "review routing. Controlled read-only tool execution is available only "
        "through the explicit server-side approval boundary."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ALLOW_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    if APP_ENV != "production":
        return ["*"]
    return []


allowed_origins = _cors_origins()
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allowed_origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)
app.include_router(rag_router)


@app.get("/", include_in_schema=False)
def root():
    """Open the dependency-free operator workspace."""
    return operator_workspace()


@app.get("/health", tags=["system"])
def health_check() -> JSONResponse:
    """Return database and RAG readiness without contacting an optional LLM."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        collection_counts = get_index_stats()
        rag_ready = bool(collection_counts) and all(
            count > 0 for count in collection_counts.values()
        )
        if not rag_ready:
            raise RuntimeError("RAG index is empty")
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "guided-agent-os",
                "version": APP_VERSION,
                "revision": GIT_REVISION,
                "database": "unavailable",
                "rag": "unavailable",
                "error": str(exc),
            },
        )

    return JSONResponse(
        content={
            "status": "healthy",
            "service": "guided-agent-os",
            "version": APP_VERSION,
            "revision": GIT_REVISION,
            "database": "ready",
            "rag": "ready",
            "collections": collection_counts,
            "llm": "optional",
        }
    )


@app.get("/version", tags=["system"])
def version_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "guided-agent-os",
        "version": APP_VERSION,
        "revision": GIT_REVISION,
        "environment": APP_ENV,
    }
