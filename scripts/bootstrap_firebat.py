from __future__ import annotations

import json
import os
from pathlib import Path

from app.models.database import Base, engine
from app.services.rag_indexer import get_index_stats, rebuild_rag_index


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:////app/data/agent_os.db")
    chroma_path = Path(os.getenv("RAG_CHROMA_PATH", "/app/data/chroma"))
    chroma_path.mkdir(parents=True, exist_ok=True)

    if database_url.startswith("sqlite:////"):
        database_path = Path(database_url.removeprefix("sqlite:////")).resolve()
        database_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)

    rebuild_on_start = os.getenv("RAG_REBUILD_ON_START", "true").lower() == "true"
    stats = get_index_stats()
    if rebuild_on_start or not stats or not all(count > 0 for count in stats.values()):
        result = rebuild_rag_index()
        stats = result["collections"]

    if not stats or not all(count > 0 for count in stats.values()):
        raise RuntimeError(f"RAG bootstrap produced empty collections: {stats}")

    print(
        json.dumps(
            {
                "status": "ready",
                "database": database_url.split("?", 1)[0],
                "chroma_path": str(chroma_path),
                "collections": stats,
                "llm": "optional",
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
