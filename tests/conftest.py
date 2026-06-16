from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path


_RAG_TEST_ROOT = Path(tempfile.mkdtemp(prefix="guided-agent-os-rag-")).resolve()
_RAG_TEST_CHROMA = _RAG_TEST_ROOT / "chroma"
os.environ.setdefault("RAG_CHROMA_PATH", str(_RAG_TEST_CHROMA))


@atexit.register
def _cleanup_rag_test_root() -> None:
    shutil.rmtree(_RAG_TEST_ROOT, ignore_errors=True)
