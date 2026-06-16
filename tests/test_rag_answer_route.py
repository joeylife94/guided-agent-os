"""
Tests for RAG Answer API Route

Tests the POST /api/rag/answer endpoint.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.rag_indexer import rebuild_rag_index


@pytest.fixture(scope="module", autouse=True)
def setup_rag_index():
    """Rebuild RAG index before running tests."""
    rebuild_rag_index()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestRAGAnswerEndpoint:
    """Test POST /api/rag/answer endpoint."""
    
    @patch("app.api.rag_routes.generate_rag_answer")
    def test_answer_endpoint_success(self, mock_generate, client):
        """Should return answer for valid request."""
        mock_generate.return_value = {
            "question": "How should the agent handle legacy DB?",
            "answer": "The agent should...",
            "citations": [
                {
                    "doc_id": "d1",
                    "title": "Database Policy",
                    "source_path": "policy.md",
                    "collection": "agent_policy",
                    "chunk_index": 0,
                    "score": 0.95,
                }
            ],
            "retrieved_context": {
                "domain_knowledge": [],
                "agent_policy": [
                    {
                        "content": "Policy content",
                        "metadata": {
                            "doc_id": "d1",
                            "title": "Database Policy",
                            "source_path": "policy.md",
                            "collection": "agent_policy",
                            "chunk_index": 0,
                        },
                        "score": 0.95,
                    }
                ],
                "tool_catalog": [],
            },
            "limitations": [
                "Answers are based only on retrieved context."
            ],
            "model": {
                "provider": "local",
                "name": "qwen2.5:7b-instruct",
                "available": True,
            },
            "error": None,
        }
        
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "How should the agent handle legacy DB?",
                "top_k_per_collection": 3,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "How should the agent handle legacy DB?"
        assert data["answer"] == "The agent should..."
        assert data["model"]["available"] is True
        assert len(data["citations"]) > 0
    
    def test_answer_endpoint_missing_question(self, client):
        """Should reject request without question."""
        response = client.post(
            "/api/rag/answer",
            json={
                "top_k_per_collection": 3,
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_answer_endpoint_empty_question(self, client):
        """Should reject request with empty question."""
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "",
                "top_k_per_collection": 3,
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_answer_endpoint_whitespace_question(self, client):
        """Should reject request with a whitespace-only question."""
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "   \n\t  ",
                "top_k_per_collection": 3,
            }
        )

        assert response.status_code == 422
    
    def test_answer_endpoint_top_k_bounds(self, client):
        """Should enforce top_k bounds."""
        # top_k too small
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "Test?",
                "top_k_per_collection": 0,
            }
        )
        assert response.status_code == 422
        
        # top_k too large
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "Test?",
                "top_k_per_collection": 11,
            }
        )
        assert response.status_code == 422
    
    def test_answer_endpoint_top_k_valid_bounds(self, client):
        """Should accept valid top_k values."""
        with patch("app.api.rag_routes.generate_rag_answer") as mock_generate:
            mock_generate.return_value = {
                "question": "Test?",
                "answer": "Answer",
                "citations": [],
                "retrieved_context": {
                    "domain_knowledge": [],
                    "agent_policy": [],
                    "tool_catalog": [],
                },
                "limitations": [],
                "model": {
                    "provider": "local",
                    "name": "model",
                    "available": True,
                },
                "error": None,
            }
            
            # Minimum valid value (1)
            response = client.post(
                "/api/rag/answer",
                json={
                    "question": "Test?",
                    "top_k_per_collection": 1,
                }
            )
            assert response.status_code == 200
            
            # Maximum valid value (10)
            response = client.post(
                "/api/rag/answer",
                json={
                    "question": "Test?",
                    "top_k_per_collection": 10,
                }
            )
            assert response.status_code == 200
    
    @patch("app.api.rag_routes.generate_rag_answer")
    def test_answer_endpoint_default_top_k(self, mock_generate, client):
        """Should use default top_k if not specified."""
        mock_generate.return_value = {
            "question": "Test?",
            "answer": "Answer",
            "citations": [],
            "retrieved_context": {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            },
            "limitations": [],
            "model": {
                "provider": "local",
                "name": "model",
                "available": True,
            },
            "error": None,
        }
        
        response = client.post(
            "/api/rag/answer",
            json={"question": "Test?"}
        )
        
        assert response.status_code == 200
        
        # Check that generate_rag_answer was called with default top_k
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["top_k_per_collection"] == 3
    
    @patch("app.api.rag_routes.generate_rag_answer")
    def test_answer_endpoint_model_override(self, mock_generate, client):
        """Should pass model parameter when provided."""
        mock_generate.return_value = {
            "question": "Test?",
            "answer": "Answer",
            "citations": [],
            "retrieved_context": {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            },
            "limitations": [],
            "model": {
                "provider": "local",
                "name": "custom-model",
                "available": True,
            },
            "error": None,
        }
        
        response = client.post(
            "/api/rag/answer",
            json={
                "question": "Test?",
                "model": "custom-model",
            }
        )
        
        assert response.status_code == 200
        
        # Check that generate_rag_answer was called with the model
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["model"] == "custom-model"

    @patch("app.api.rag_routes.generate_rag_answer")
    def test_answer_endpoint_blank_model_uses_default(self, mock_generate, client):
        """Blank model override should be normalized to the default."""
        mock_generate.return_value = {
            "question": "Test?",
            "answer": "Answer",
            "citations": [],
            "retrieved_context": {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            },
            "limitations": [],
            "model": {
                "provider": "local",
                "name": "default-model",
                "available": True,
            },
            "error": None,
        }

        response = client.post(
            "/api/rag/answer",
            json={
                "question": "Test?",
                "model": "   ",
            }
        )

        assert response.status_code == 200
        assert mock_generate.call_args[1]["model"] is None
    
    @patch("app.api.rag_routes.generate_rag_answer")
    def test_answer_endpoint_llm_unavailable(self, mock_generate, client):
        """Should return 200 with fallback when LLM is unavailable."""
        mock_generate.return_value = {
            "question": "Test?",
            "answer": "Local LLM is unavailable. Retrieved context is returned for review.",
            "citations": [],
            "retrieved_context": {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            },
            "limitations": [],
            "model": {
                "provider": "local",
                "name": "qwen2.5:7b-instruct",
                "available": False,
            },
            "error": "Connection refused",
        }
        
        response = client.post(
            "/api/rag/answer",
            json={"question": "Test?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["model"]["available"] is False
        assert "unavailable" in data["answer"].lower()
    
    def test_answer_endpoint_response_structure(self, client):
        """Should return properly structured response."""
        with patch("app.api.rag_routes.generate_rag_answer") as mock_generate:
            mock_generate.return_value = {
                "question": "Test question?",
                "answer": "Test answer",
                "citations": [
                    {
                        "doc_id": "d1",
                        "title": "Title",
                        "source_path": "file.md",
                        "collection": "domain_knowledge",
                        "chunk_index": 0,
                        "score": 0.9,
                    }
                ],
                "retrieved_context": {
                    "domain_knowledge": [
                        {
                            "content": "Content",
                            "metadata": {
                                "doc_id": "d1",
                                "title": "Title",
                                "source_path": "file.md",
                                "collection": "domain_knowledge",
                                "chunk_index": 0,
                            },
                            "score": 0.9,
                        }
                    ],
                    "agent_policy": [],
                    "tool_catalog": [],
                },
                "limitations": ["Limitation 1"],
                "model": {
                    "provider": "local",
                    "name": "qwen2.5:7b-instruct",
                    "available": True,
                },
                "error": None,
            }
            
            response = client.post(
                "/api/rag/answer",
                json={"question": "Test question?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "question" in data
            assert "answer" in data
            assert "citations" in data
            assert isinstance(data["citations"], list)
            assert "retrieved_context" in data
            assert "limitations" in data
            assert isinstance(data["limitations"], list)
            assert "model" in data
            assert data["model"]["provider"] == "local"
