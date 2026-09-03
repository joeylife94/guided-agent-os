from app.operator_evidence_ui import operator_workspace_with_evidence


def test_operator_evidence_contains_retrieval_provenance_summary_contract() -> None:
    html = operator_workspace_with_evidence().body.decode("utf-8")

    assert 'id="retrieval-provenance-summary"' in html
    assert 'id="retrieval-embedding-provider"' in html
    assert 'id="retrieval-embedding-model"' in html
    assert 'id="retrieval-embedding-dimensions"' in html
    assert "event.event_type === 'RAG_RETRIEVED'" in html
    assert "payload.embedding_provider" in html
    assert "payload.embedding_model" in html
    assert "payload.embedding_dimensions" in html
    assert "Retrieval provenance unavailable." in html
    assert "renderRetrievalProvenance(evidence)" in html
    assert "clearRetrievalProvenance()" in html
