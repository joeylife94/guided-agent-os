"""
Tests for RAG Document Loader

Tests document discovery, collection mapping, and chunking.
"""

import pytest
from pathlib import Path
from app.services.rag_document_loader import (
    discover_markdown_files,
    load_and_chunk_documents,
    get_collection_names,
    _split_into_chunks,
    _generate_deterministic_id,
    get_knowledge_base_path,
)


class TestDocumentDiscovery:
    """Test document discovery functionality."""
    
    def test_knowledge_base_path_exists(self):
        """Knowledge base directory should exist."""
        path = get_knowledge_base_path()
        assert path.exists()
        assert path.is_dir()
    
    def test_discover_markdown_files(self):
        """Should discover markdown files in knowledge directory."""
        files = discover_markdown_files()
        assert isinstance(files, list)
        assert len(files) > 0
        
        # Check structure of discovered files
        for file_info in files:
            assert "full_path" in file_info
            assert "relative_path" in file_info
            assert "collection" in file_info
            assert "title" in file_info
            assert file_info["full_path"].exists()
    
    def test_collection_mapping(self):
        """Files should be mapped to correct collections."""
        files = discover_markdown_files()
        collections_found = set()
        
        for file_info in files:
            collections_found.add(file_info["collection"])
            assert file_info["collection"] in get_collection_names()
        
        # Should find all three collections
        assert len(collections_found) == 3


class TestChunking:
    """Test document chunking functionality."""
    
    def test_chunk_size_respected(self):
        """Chunks should not exceed specified size."""
        text = "x" * 2000  # Create text larger than chunk size
        chunk_size = 800
        chunks = _split_into_chunks(text, chunk_size=chunk_size, overlap=120)
        
        for chunk in chunks:
            assert len(chunk) <= chunk_size + 100  # Allow small overshoot
    
    def test_overlap_applied(self):
        """Chunks should have overlap between them."""
        text = "abcdefghijklmnopqrstuvwxyz" * 100
        chunks = _split_into_chunks(text, chunk_size=800, overlap=120)
        
        assert len(chunks) > 1
        # Check that consecutive chunks have overlap
        for i in range(len(chunks) - 1):
            # Some characters from end of chunk i should appear in chunk i+1
            overlap_found = chunks[i + 1][:100] in chunks[i] or \
                            chunks[i][-100:] in chunks[i + 1]
            assert overlap_found
    
    def test_empty_content(self):
        """Empty content should return empty list."""
        chunks = _split_into_chunks("", chunk_size=800)
        assert chunks == []

    def test_whitespace_content(self):
        """Whitespace-only content should return empty list."""
        chunks = _split_into_chunks("   \n\t  ", chunk_size=800)
        assert chunks == []
    
    def test_small_content(self):
        """Small content should return single chunk."""
        text = "This is small content."
        chunks = _split_into_chunks(text, chunk_size=800)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_overlap_cannot_create_infinite_loop(self):
        """Overlap greater than chunk size should still terminate."""
        text = "abcdef" * 50
        chunks = _split_into_chunks(text, chunk_size=10, overlap=10)

        assert chunks
        assert all(chunk.strip() for chunk in chunks)
        assert all(len(chunk) <= 10 for chunk in chunks)

    def test_invalid_chunk_size_is_clamped(self):
        """Invalid chunk size should not produce empty chunks or hang."""
        chunks = _split_into_chunks("abc", chunk_size=0, overlap=5)

        assert chunks == ["a", "b", "c"]


class TestDeterministicIDs:
    """Test deterministic ID generation."""
    
    def test_id_generation(self):
        """IDs should be generated consistently."""
        collection = "test_collection"
        path = "test/file.md"
        index = 0
        
        id1 = _generate_deterministic_id(collection, path, index)
        id2 = _generate_deterministic_id(collection, path, index)
        
        assert id1 == id2  # Same inputs should produce same ID
    
    def test_id_differs_by_index(self):
        """Different indices should produce different IDs."""
        collection = "test_collection"
        path = "test/file.md"
        
        id1 = _generate_deterministic_id(collection, path, 0)
        id2 = _generate_deterministic_id(collection, path, 1)
        
        assert id1 != id2


class TestLoadAndChunk:
    """Test full document loading and chunking."""
    
    def test_load_and_chunk_documents(self):
        """Should load and chunk all documents."""
        chunks = load_and_chunk_documents()
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
    
    def test_chunk_metadata(self):
        """Each chunk should have required metadata."""
        chunks = load_and_chunk_documents()
        
        for chunk in chunks:
            assert "doc_id" in chunk
            assert "content" in chunk
            assert "metadata" in chunk
            
            # Check metadata contents
            meta = chunk["metadata"]
            assert "doc_id" in meta
            assert "title" in meta
            assert "source_path" in meta
            assert "collection" in meta
            assert "chunk_index" in meta
            
            # Metadata should match chunk doc_id
            assert meta["doc_id"] == chunk["doc_id"]
    
    def test_chunks_have_content(self):
        """All chunks should have non-empty content."""
        chunks = load_and_chunk_documents()
        
        for chunk in chunks:
            assert chunk["content"]
            assert len(chunk["content"].strip()) > 0
    
    def test_chunks_in_correct_collections(self):
        """Chunks should be assigned to valid collections."""
        chunks = load_and_chunk_documents()
        valid_collections = get_collection_names()
        
        for chunk in chunks:
            assert chunk["metadata"]["collection"] in valid_collections


class TestCollectionNames:
    """Test collection name functionality."""
    
    def test_get_collection_names(self):
        """Should return all collection names."""
        names = get_collection_names()
        
        assert isinstance(names, list)
        assert len(names) == 3
        assert "domain_knowledge" in names
        assert "agent_policy" in names
        assert "tool_catalog" in names
