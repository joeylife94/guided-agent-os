"""
Tests for RAG Answerer Service

Tests the RAG answer generation pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.rag_answerer import (
    generate_rag_answer,
    _build_context_block,
    _build_system_prompt,
    _validate_question,
    _validate_top_k_per_collection,
)
from app.services.local_llm import LocalLLMClient
from app.services.rag_indexer import rebuild_rag_index


@pytest.fixture(scope="module", autouse=True)
def setup_rag_index():
    """Rebuild RAG index before running tests."""
    rebuild_rag_index()


class TestBuildContextBlock:
    """Test context block builder."""
    
    def test_empty_context(self):
        """Should handle empty retrieved context."""
        result = _build_context_block({
            "domain_knowledge": [],
            "agent_policy": [],
            "tool_catalog": [],
        })
        # Should return empty or minimal string
        assert isinstance(result, str)
    
    def test_single_result(self):
        """Should format single result correctly."""
        context = {
            "domain_knowledge": [
                {
                    "content": "This is a test document.",
                    "metadata": {
                        "title": "Test Title",
                        "doc_id": "doc1",
                        "source_path": "test.md",
                        "collection": "domain_knowledge",
                        "chunk_index": 0,
                    },
                    "score": 0.95,
                }
            ],
            "agent_policy": [],
            "tool_catalog": [],
        }
        result = _build_context_block(context)
        
        assert "Test Title" in result
        assert "This is a test document." in result
    
    def test_multiple_results_multiple_collections(self):
        """Should handle multiple results from multiple collections."""
        context = {
            "domain_knowledge": [
                {
                    "content": "Domain content 1",
                    "metadata": {
                        "title": "Domain Doc 1",
                        "doc_id": "d1",
                        "source_path": "d1.md",
                        "collection": "domain_knowledge",
                        "chunk_index": 0,
                    },
                    "score": 0.9,
                },
                {
                    "content": "Domain content 2",
                    "metadata": {
                        "title": "Domain Doc 2",
                        "doc_id": "d2",
                        "source_path": "d2.md",
                        "collection": "domain_knowledge",
                        "chunk_index": 0,
                    },
                    "score": 0.85,
                },
            ],
            "agent_policy": [
                {
                    "content": "Policy content",
                    "metadata": {
                        "title": "Policy Doc",
                        "doc_id": "p1",
                        "source_path": "p1.md",
                        "collection": "agent_policy",
                        "chunk_index": 0,
                    },
                    "score": 0.88,
                }
            ],
            "tool_catalog": [],
        }
        result = _build_context_block(context)
        
        assert "Domain Knowledge" in result or "domain" in result.lower()
        assert "Agent Policy" in result or "agent policy" in result.lower()
        assert "Domain content 1" in result
        assert "Domain content 2" in result
        assert "Policy content" in result


class TestBuildSystemPrompt:
    """Test system prompt builder."""
    
    def test_system_prompt_content(self):
        """Should include critical rules."""
        prompt = _build_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "controlled Guided Agent OS assistant" in prompt
        assert "retrieved context" in prompt.lower()
        assert "do not invent" in prompt.lower() or "don't invent" in prompt.lower()
        assert "do not claim" in prompt.lower()
        assert "sql" in prompt.lower()


class TestInputValidation:
    """Test service-level request validation."""

    def test_validate_question_strips_whitespace(self):
        """Question validation should normalize surrounding whitespace."""
        assert _validate_question("  What is allowed?  ") == "What is allowed?"

    def test_validate_question_rejects_blank(self):
        """Blank questions should be rejected before retrieval."""
        with pytest.raises(ValueError):
            _validate_question("   \n\t  ")

    def test_validate_top_k_bounds(self):
        """Answer generation should enforce the Phase 2 top_k bounds."""
        assert _validate_top_k_per_collection(1) == 1
        assert _validate_top_k_per_collection(10) == 10

        with pytest.raises(ValueError):
            _validate_top_k_per_collection(0)

        with pytest.raises(ValueError):
            _validate_top_k_per_collection(11)


class TestGenerateRAGAnswer:
    """Test RAG answer generation."""
    
    def test_returns_required_fields(self):
        """Should return all required fields in response."""
        # Mock the LLM client
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": "This is a test answer.",
        }
        
        result = generate_rag_answer(
            question="What is a test?",
            llm_client=mock_llm,
        )
        
        # Check required fields
        assert "question" in result
        assert "answer" in result
        assert "citations" in result
        assert "retrieved_context" in result
        assert "limitations" in result
        assert "model" in result
        
        # Check model metadata structure
        assert "provider" in result["model"]
        assert "name" in result["model"]
        assert "available" in result["model"]
    
    def test_answer_from_successful_llm(self):
        """Should use LLM response when available."""
        mock_llm = Mock(spec=LocalLLMClient)
        llm_response = "The answer to your question is..."
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": llm_response,
        }
        
        result = generate_rag_answer(
            question="Test question?",
            llm_client=mock_llm,
        )
        
        assert result["answer"] == llm_response
        assert result["model"]["available"] is True
        assert result["error"] is None
    
    def test_fallback_when_llm_unavailable(self):
        """Should use fallback message when LLM is unavailable."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": False,
            "model": "qwen2.5:7b-instruct",
            "content": "",
            "error": "Connection refused",
        }
        
        result = generate_rag_answer(
            question="Test question?",
            llm_client=mock_llm,
        )
        
        assert result["model"]["available"] is False
        assert "Local LLM is unavailable" in result["answer"]
        assert result["error"] == "Connection refused"

    def test_fallback_when_llm_raises(self):
        """Unexpected local LLM client errors should not crash answer generation."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.model = "qwen2.5:7b-instruct"
        mock_llm.chat.side_effect = RuntimeError("boom")

        with patch("app.services.rag_answerer.retrieve_from_all_collections") as mock_retrieve:
            mock_retrieve.return_value = {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            }

            result = generate_rag_answer(
                question="Test question?",
                llm_client=mock_llm,
            )

        assert result["model"]["available"] is False
        assert "Local LLM is unavailable" in result["answer"]
        assert "Unexpected local LLM client error" in result["error"]
    
    def test_citations_from_retrieved_context(self):
        """Should extract citations from retrieved context."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": "Answer based on context.",
        }
        
        with patch("app.services.rag_answerer.retrieve_from_all_collections") as mock_retrieve:
            mock_retrieve.return_value = {
                "domain_knowledge": [
                    {
                        "content": "Knowledge content",
                        "metadata": {
                            "doc_id": "d1",
                            "title": "Doc 1",
                            "source_path": "doc1.md",
                            "collection": "domain_knowledge",
                            "chunk_index": 0,
                        },
                        "score": 0.95,
                    }
                ],
                "agent_policy": [],
                "tool_catalog": [],
            }
            
            result = generate_rag_answer(
                question="Test?",
                llm_client=mock_llm,
            )
            
            assert len(result["citations"]) == 1
            citation = result["citations"][0]
            assert citation["doc_id"] == "d1"
            assert citation["title"] == "Doc 1"
            assert citation["collection"] == "domain_knowledge"

    def test_question_is_stripped_before_retrieval_and_response(self):
        """Question whitespace should be normalized consistently."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": "Answer",
        }

        with patch("app.services.rag_answerer.retrieve_from_all_collections") as mock_retrieve:
            mock_retrieve.return_value = {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            }

            result = generate_rag_answer(
                question="  Test?  ",
                llm_client=mock_llm,
            )

            assert result["question"] == "Test?"
            assert mock_retrieve.call_args[1]["query"] == "Test?"
    
    def test_limitations_always_present(self):
        """Should always include limitations."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": "Answer",
        }
        
        result = generate_rag_answer(
            question="Test?",
            llm_client=mock_llm,
        )
        
        assert isinstance(result["limitations"], list)
        assert len(result["limitations"]) > 0
        assert any("generated only from retrieved" in l.lower() for l in result["limitations"])
        assert any("no real tool" in l.lower() or "tool" in l.lower() for l in result["limitations"])
    
    def test_top_k_parameter(self):
        """Should pass top_k_per_collection to retriever."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": True,
            "model": "qwen2.5:7b-instruct",
            "content": "Answer",
        }
        
        with patch("app.services.rag_answerer.retrieve_from_all_collections") as mock_retrieve:
            mock_retrieve.return_value = {
                "domain_knowledge": [],
                "agent_policy": [],
                "tool_catalog": [],
            }
            
            generate_rag_answer(
                question="Test?",
                top_k_per_collection=5,
                llm_client=mock_llm,
            )
            
            mock_retrieve.assert_called_once()
            call_kwargs = mock_retrieve.call_args[1]
            assert call_kwargs["top_k_per_collection"] == 5
    
    def test_retrieved_context_preserved_on_failure(self):
        """Should include retrieved context even if LLM fails."""
        mock_llm = Mock(spec=LocalLLMClient)
        mock_llm.chat.return_value = {
            "ok": False,
            "model": "qwen2.5:7b-instruct",
            "content": "",
            "error": "Connection refused",
        }
        
        with patch("app.services.rag_answerer.retrieve_from_all_collections") as mock_retrieve:
            mock_retrieve.return_value = {
                "domain_knowledge": [
                    {
                        "content": "Important context",
                        "metadata": {
                            "doc_id": "d1",
                            "title": "Doc 1",
                            "source_path": "doc1.md",
                            "collection": "domain_knowledge",
                            "chunk_index": 0,
                        },
                        "score": 0.9,
                    }
                ],
                "agent_policy": [],
                "tool_catalog": [],
            }
            
            result = generate_rag_answer(
                question="Test?",
                llm_client=mock_llm,
            )
            
            # Should still have context
            assert "domain_knowledge" in result["retrieved_context"]
            assert len(result["retrieved_context"]["domain_knowledge"]) > 0
            assert result["retrieved_context"]["domain_knowledge"][0]["content"] == "Important context"
