from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.rag_routes import router as rag_router
from app.models.database import Base, engine

# ---------------------------------------------------------------------------
# Create all tables on startup (idempotent)
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Guided Agent OS",
    description=(
        "A guided intake and controlled RAG agent platform that validates "
        "required fields, asks clarification questions, normalizes input, "
        "persists runs, and supports a controlled_rag_agent workflow with "
        "local grounded RAG answers, planned-only tool/API plans, and human "
        "review routing. It does not execute SQL, tools, APIs, or external "
        "account actions."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — open during development; tighten for production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(router)
app.include_router(rag_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Returns a simple liveness signal."""
    return {"status": "ok", "service": "guided-agent-os"}
