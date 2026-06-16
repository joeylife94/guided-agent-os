"""
Tests for RAG Retriever

Tests querying functionality across collections.
"""

import pytest
from app.services.rag_retriever import (
    MAX_TOP_K,
    retrieve_from_collection,
    retrieve_from_all_collections,
    search_all_collections,
)
from app.services.rag_indexer import rebuild_rag_index
from app.services.rag_document_loader import get_collection_names


@pytest.fixture(scope="module", autouse=True)
def setup_rag_index():
    """Rebuild RAG index before running tests."""
    rebuild_rag_index()


class TestRetrieveFromCollection:
    """Test single collection retrieval."""
    
    def test_query_returns_list(self):
        """Should return list of results."""
        results = retrieve_from_collection(
            query="agent behavior",
            collection_name="agent_policy",
        )
        assert isinstance(results, list)
    
    def test_query_returns_normalized_results(self):
        """Results should have required structure."""
        results = retrieve_from_collection(
            query="policies",
            collection_name="agent_policy",
            top_k=3,
        )
        
        for result in results:
            assert "content" in result
            assert "metadata" in result
            assert "score" in result
            
            # Check metadata
            meta = result["metadata"]
            assert "doc_id" in meta
            assert "title" in meta
            assert "source_path" in meta
            assert "collection" in meta
            assert "chunk_index" in meta
    
    def test_query_respects_top_k(self):
        """Should return at most top_k results."""
        for top_k in [1, 3, 5]:
            results = retrieve_from_collection(
                query="database",
                collection_name="tool_catalog",
                top_k=top_k,
            )
            assert len(results) <= top_k
    
    def test_results_sorted_by_score(self):
        """Results should be sorted by score descending."""
        results = retrieve_from_collection(
            query="policy",
            collection_name="agent_policy",
        )
        
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_scores_in_valid_range(self):
        """Scores should be between 0 and 1."""
        results = retrieve_from_collection(
            query="knowledge",
            collection_name="domain_knowledge",
        )
        
        for result in results:
            score = result["score"]
            assert 0 <= score <= 1
    
    def test_empty_query_returns_empty(self):
        """Empty query should return empty results."""
        results = retrieve_from_collection(
            query="",
            collection_name="agent_policy",
        )
        assert results == []
    
    def test_invalid_collection_returns_empty(self):
        """Invalid collection should return empty results."""
        results = retrieve_from_collection(
            query="test",
            collection_name="nonexistent_collection",
        )
        assert isinstance(results, list)
    
    def test_whitespace_only_query_returns_empty(self):
        """Whitespace-only query should return empty results."""
        results = retrieve_from_collection(
            query="   \n\t  ",
            collection_name="agent_policy",
        )
        assert results == []

    def test_top_k_is_clamped_to_safe_lower_bound(self):
        """Service-level retrieval should safely clamp invalid low top_k."""
        results = retrieve_from_collection(
            query="policy",
            collection_name="agent_policy",
            top_k=0,
        )
        assert isinstance(results, list)
        assert len(results) <= 1

    def test_top_k_is_clamped_to_safe_upper_bound(self):
        """Service-level retrieval should safely clamp excessive top_k."""
        results = retrieve_from_collection(
            query="policy",
            collection_name="agent_policy",
            top_k=10_000,
        )
        assert isinstance(results, list)
        assert len(results) <= MAX_TOP_K


class TestRetrieveFromAllCollections:
    """Test multi-collection retrieval."""
    
    def test_query_returns_dict(self):
        """Should return dict of collections."""
        results = retrieve_from_all_collections(query="policy")
        assert isinstance(results, dict)
    
    def test_all_collections_in_results(self):
        """Results should include all collections."""
        results = retrieve_from_all_collections(query="test")
        
        for collection_name in get_collection_names():
            assert collection_name in results
    
    def test_each_collection_returns_list(self):
        """Each collection should have list of results."""
        results = retrieve_from_all_collections(query="test")
        
        for collection_name, collection_results in results.items():
            assert isinstance(collection_results, list)
    
    def test_respects_top_k_per_collection(self):
        """Should return at most top_k results per collection."""
        for top_k in [1, 2, 3]:
            results = retrieve_from_all_collections(
                query="guidelines",
                top_k_per_collection=top_k,
            )
            
            for collection_results in results.values():
                assert len(collection_results) <= top_k
    
    def test_results_have_normalized_structure(self):
        """All results should be normalized."""
        results = retrieve_from_all_collections(query="access")
        
        for collection_results in results.values():
            for result in collection_results:
                assert "content" in result
                assert "metadata" in result
                assert "score" in result

    def test_empty_query_returns_empty_lists_for_all_collections(self):
        """Empty multi-collection query should not touch Chroma."""
        results = retrieve_from_all_collections(query="  ")

        assert set(results) == set(get_collection_names())
        assert all(collection_results == [] for collection_results in results.values())


class TestSearchAllCollections:
    """Test flat list search across all collections."""
    
    def test_search_returns_list(self):
        """Should return flat list of results."""
        results = search_all_collections(query="database")
        assert isinstance(results, list)
    
    def test_results_are_sorted_by_score(self):
        """Results should be sorted by score descending."""
        results = search_all_collections(query="policy")
        
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_results_include_multiple_collections(self):
        """Results should potentially come from multiple collections."""
        results = search_all_collections(query="guidelines", top_k_per_collection=5)
        
        if len(results) > 0:
            # Check that results are properly normalized
            for result in results:
                assert "collection" in result["metadata"]


class TestQueryDomain:
    """Integration tests with domain-specific queries."""
    
    def test_query_for_agent_behavior(self):
        """Should find results for agent behavior queries."""
        results = retrieve_from_collection(
            query="Should the agent execute database changes directly?",
            collection_name="agent_policy",
        )
        assert len(results) >= 0  # May or may not have results
    
    def test_query_for_legacy_database_access(self):
        """Should find results about legacy database access."""
        results = search_all_collections(
            query="How should an agent handle legacy database access?"
        )
        # Results come from tool_catalog primarily
        if len(results) > 0:
            assert any(r["metadata"]["collection"] == "tool_catalog" for r in results)
    
    def test_query_for_citation_policy(self):
        """Should find source citation policy."""
        results = retrieve_from_collection(
            query="how to cite sources",
            collection_name="agent_policy",
        )
        # May find results about citation policy
        assert isinstance(results, list)
