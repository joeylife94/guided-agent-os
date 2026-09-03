from pathlib import Path


def test_p024_browser_retrieval_provenance_workflow_contract() -> None:
    workflow = Path(".github/workflows/p024-retrieval-provenance.yml")
    assert workflow.exists(), "P-024 requires a dedicated browser proof workflow"

    text = workflow.read_text(encoding="utf-8")
    assert "P-024 Browser Retrieval Provenance" in text
    assert "retrieval-embedding-provider" in text
    assert "retrieval-embedding-model" in text
    assert "retrieval-embedding-dimensions" in text
    assert "Retrieval provenance unavailable." in text
    assert "RAG_RETRIEVED" in text
    assert "embedding_provider" in text
    assert "embedding_model" in text
    assert "embedding_dimensions" in text
