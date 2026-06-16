"""
Tests for RAG FastAPI Routes

Tests the REST API endpoints for RAG functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag_indexer import rebuild_rag_index


@pytest.fixture(scope="module", autouse=True)
def setup_rag_index():
    """Rebuild RAG index before running tests."""
    rebuild_rag_index()


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


class TestRebuildIndexEndpoint:
    """Test POST /api/rag/rebuild-index endpoint."""
    
    def test_rebuild_index_success(self, client):
        """Should rebuild index successfully."""
        response = client.post("/api/rag/rebuild-index")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "collections" in data
        assert data["status"] == "indexed"
    
    def test_rebuild_index_returns_collections(self, client):
        """Should return all three collections."""
        response = client.post("/api/rag/rebuild-index")
        data = response.json()
        
        collections = data["collections"]
        assert "domain_knowledge" in collections
        assert "agent_policy" in collections
        assert "tool_catalog" in collections
    
    def test_rebuild_index_collection_counts_are_integers(self, client):
        """Collection counts should be integers."""
        response = client.post("/api/rag/rebuild-index")
        data = response.json()
        
        for count in data["collections"].values():
            assert isinstance(count, int)
            assert count >= 0


class TestQueryCollectionEndpoint:
    """Test GET /api/rag/query endpoint."""
    
    def test_query_requires_q_parameter(self, client):
        """Should require q parameter."""
        response = client.get("/api/rag/query")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_query_with_valid_parameters(self, client):
        """Should query with valid parameters."""
        response = client.get(
            "/api/rag/query",
            params={
                "q": "agent policy",
                "collection": "agent_policy",
                "top_k": 3,
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "collection" in data
        assert "results" in data
    
    def test_query_default_collection(self, client):
        """Should use default collection if not specified."""
        response = client.get(
            "/api/rag/query",
            params={"q": "test query"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["collection"] == "domain_knowledge"
    
    def test_query_respects_top_k(self, client):
        """Should respect top_k parameter."""
        response = client.get(
            "/api/rag/query",
            params={
                "q": "test",
                "collection": "agent_policy",
                "top_k": 2,
            }
        )
        data = response.json()
        assert len(data["results"]) <= 2
    
    def test_query_top_k_bounds(self, client):
        """Should enforce top_k bounds."""
        # top_k > max bound should be rejected
        response = client.get(
            "/api/rag/query",
            params={
                "q": "test",
                "top_k": 100,
            }
        )
        assert response.status_code == 422

        response = client.get(
            "/api/rag/query",
            params={
                "q": "test",
                "top_k": 0,
            }
        )
        assert response.status_code == 422

    def test_query_rejects_whitespace_query(self, client):
        """Whitespace-only q should be rejected safely."""
        response = client.get(
            "/api/rag/query",
            params={
                "q": "   \n\t  ",
                "collection": "agent_policy",
            }
        )
        assert response.status_code == 400
    
    def test_query_invalid_collection(self, client):
        """Should reject invalid collection."""
        response = client.get(
            "/api/rag/query",
            params={
                "q": "test",
                "collection": "invalid_collection",
            }
        )
        assert response.status_code == 400
    
    def test_query_returns_normalized_results(self, client):
        """Results should be normalized."""
        response = client.get(
            "/api/rag/query",
            params={
                "q": "policy",
                "collection": "agent_policy",
            }
        )
        data = response.json()
        
        for result in data["results"]:
            assert "content" in result
            assert "metadata" in result
            assert "score" in result


class TestQueryAllCollectionsEndpoint:
    """Test GET /api/rag/query-all endpoint."""
    
    def test_query_all_requires_q_parameter(self, client):
        """Should require q parameter."""
        response = client.get("/api/rag/query-all")
        assert response.status_code == 422
    
    def test_query_all_with_valid_parameters(self, client):
        """Should query all collections."""
        response = client.get(
            "/api/rag/query-all",
            params={
                "q": "test query",
                "top_k": 3,
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "results" in data
    
    def test_query_all_returns_all_collections(self, client):
        """Should return results from all collections."""
        response = client.get(
            "/api/rag/query-all",
            params={"q": "guidelines"}
        )
        data = response.json()
        results = data["results"]
        
        assert "domain_knowledge" in results
        assert "agent_policy" in results
        assert "tool_catalog" in results
    
    def test_query_all_respects_top_k(self, client):
        """Should respect top_k per collection."""
        response = client.get(
            "/api/rag/query-all",
            params={
                "q": "test",
                "top_k": 2,
            }
        )
        data = response.json()
        
        for collection_results in data["results"].values():
            assert len(collection_results) <= 2

    def test_query_all_rejects_whitespace_query(self, client):
        """Whitespace-only q should be rejected safely."""
        response = client.get(
            "/api/rag/query-all",
            params={"q": "   \n\t  "}
        )
        assert response.status_code == 400

class TestRagEndpointScope:
    """Test that only Phase 1 RAG endpoints are exposed."""

    def test_stats_endpoint_is_not_public_phase_1_surface(self, client):
        """Stats is not part of the requested Phase 1 API contract."""
        response = client.get("/api/rag/stats")
        assert response.status_code == 404


class TestIntegration:
    """Integration tests for RAG endpoints."""
    
    def test_rebuild_then_query_workflow(self, client):
        """Should be able to rebuild index then query."""
        # Rebuild
        rebuild_response = client.post("/api/rag/rebuild-index")
        assert rebuild_response.status_code == 200
        
        # Query
        query_response = client.get(
            "/api/rag/query-all",
            params={"q": "behavior"}
        )
        assert query_response.status_code == 200
    
    def test_domain_specific_query_workflow(self, client):
        """Should handle domain-specific queries."""
        response = client.get(
            "/api/rag/query-all",
            params={
                "q": "How should an AI agent handle database access safely?",
                "top_k": 2,
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have query and results
        assert "query" in data
        assert data["query"]  # Query should not be empty
        assert "results" in data
