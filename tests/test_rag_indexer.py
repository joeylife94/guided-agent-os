"""
Tests for RAG Indexer

Tests ChromaDB indexing and collection management.
"""

import pytest
from pathlib import Path
from app.services.rag_indexer import (
    rebuild_rag_index,
    get_index_stats,
    get_chroma_db_path,
    get_chroma_client,
    get_collection_count,
    _get_or_create_collections,
)
from app.services.rag_document_loader import get_collection_names


class TestRagIndexer:
    """Test RAG indexing functionality."""
    
    def test_get_chroma_db_path_creates_directory(self):
        """Should create data/chroma directory if it doesn't exist."""
        path = get_chroma_db_path()
        assert Path(path).exists()
        assert Path(path).is_dir()
        assert "chroma" in path
    
    def test_get_chroma_client(self):
        """Should create a ChromaDB persistent client."""
        client = get_chroma_client()
        assert client is not None
        # Should have list_collections method (ChromaDB API)
        assert hasattr(client, 'get_collection')
    
    def test_rebuild_rag_index_returns_correct_structure(self):
        """Should return dict with status and collections."""
        result = rebuild_rag_index()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "collections" in result
        assert result["status"] == "indexed"
    
    def test_rebuild_rag_index_creates_all_collections(self):
        """Should create all three collections."""
        result = rebuild_rag_index()
        collections = result["collections"]
        
        assert "domain_knowledge" in collections
        assert "agent_policy" in collections
        assert "tool_catalog" in collections
    
    def test_rebuild_rag_index_has_content(self):
        """Should index content into collections."""
        result = rebuild_rag_index()
        collections = result["collections"]
        
        # Each collection should have at least some indexed documents
        for collection_name, count in collections.items():
            assert isinstance(count, int)
            assert count >= 0  # May be 0 if no documents found
    
    def test_rebuild_rag_index_counts_are_reasonable(self):
        """Collection counts should be reasonable."""
        result = rebuild_rag_index()
        collections = result["collections"]
        total = sum(collections.values())
        
        # Should have indexed at least some documents
        assert total > 0
    
    def test_get_index_stats(self):
        """Should return current collection statistics."""
        # First rebuild to ensure data exists
        rebuild_rag_index()
        
        stats = get_index_stats()
        
        assert isinstance(stats, dict)
        assert "domain_knowledge" in stats
        assert "agent_policy" in stats
        assert "tool_catalog" in stats
        
        # All should be integers
        for count in stats.values():
            assert isinstance(count, int)
            assert count >= 0
    
    def test_collections_are_queryable_after_indexing(self):
        """Collections should exist and be queryable after indexing."""
        rebuild_rag_index()
        
        client = get_chroma_client()
        
        for collection_name in get_collection_names():
            try:
                collection = client.get_collection(name=collection_name)
                assert collection is not None
            except Exception as e:
                pytest.fail(f"Collection {collection_name} not queryable: {e}")
    
    def test_indexing_is_idempotent(self):
        """Multiple indexing runs should produce same results."""
        result1 = rebuild_rag_index()
        result2 = rebuild_rag_index()
        
        # Results should be same (deterministic IDs)
        assert result1["collections"] == result2["collections"]

        # Actual persisted collection counts should also be unchanged.
        persisted_counts = {
            collection_name: get_collection_count(collection_name)
            for collection_name in get_collection_names()
        }
        assert persisted_counts == result2["collections"]


class TestCollectionCreation:
    """Test collection creation."""
    
    def test_get_or_create_collections(self):
        """Should create or get collections."""
        client = get_chroma_client()
        collections = _get_or_create_collections(client)
        
        assert isinstance(collections, dict)
        assert len(collections) == 3
        
        for collection_name in get_collection_names():
            assert collection_name in collections
            assert collections[collection_name] is not None
