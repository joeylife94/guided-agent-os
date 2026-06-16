"""
RAG Document Loader Service

Discovers, loads, and chunks Markdown files from the knowledge directory structure.
Maps directory to collection names and attaches metadata to chunks.
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Any


# Directory to collection name mapping
COLLECTION_MAPPING = {
    "domain": "domain_knowledge",
    "policies": "agent_policy",
    "tools": "tool_catalog",
}


def get_knowledge_base_path() -> Path:
    """
    Get the absolute path to the knowledge base directory.
    
    Returns:
        Path to app/knowledge/ directory
    """
    app_dir = Path(__file__).parent.parent
    return app_dir / "knowledge"


def discover_markdown_files() -> List[Dict[str, Any]]:
    """
    Discover all markdown files in the knowledge base directory.
    
    Returns a list of file info dicts with:
    - path: relative path from knowledge base
    - full_path: absolute path
    - collection: mapped collection name
    - title: extracted from filename or first heading
    """
    knowledge_path = get_knowledge_base_path()
    
    if not knowledge_path.exists():
        return []
    
    files = []
    
    for collection_dir, collection_name in COLLECTION_MAPPING.items():
        collection_path = knowledge_path / collection_dir
        
        if not collection_path.exists():
            continue
        
        for md_file in sorted(collection_path.glob("*.md"), key=lambda path: path.name):
            title = md_file.stem.replace("-", " ").title()
            
            files.append({
                "full_path": md_file,
                "relative_path": f"{collection_dir}/{md_file.name}",
                "collection": collection_name,
                "title": title,
            })
    
    return files


def _split_into_chunks(
    content: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> List[str]:
    """
    Split text content into overlapping chunks.
    
    Args:
        content: Full text to split
        chunk_size: Target size per chunk (characters)
        overlap: Overlap between consecutive chunks (characters)
    
    Returns:
        List of text chunks
    """
    content = content.strip()
    if not content:
        return []

    chunk_size = max(1, int(chunk_size))
    overlap = max(0, int(overlap))
    if chunk_size == 1:
        overlap = 0
    else:
        overlap = min(overlap, chunk_size - 1)

    if len(content) <= chunk_size:
        return [content]
    
    chunks = []
    start = 0
    content_length = len(content)

    while start < content_length:
        end = min(start + chunk_size, content_length)
        chunk = content[start:end].strip()
        if chunk.strip():
            chunks.append(chunk)
        
        if end >= content_length:
            break

        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        start = next_start
    
    return chunks


def _generate_deterministic_id(
    collection: str,
    source_path: str,
    chunk_index: int,
) -> str:
    """
    Generate a deterministic ID for a chunk to avoid duplicates.
    
    Uses SHA256 hash of (collection, source_path, chunk_index) for reproducibility.
    """
    key = f"{collection}:{source_path}:{chunk_index}"
    hash_val = hashlib.sha256(key.encode()).hexdigest()[:12]
    return f"{collection}_{hash_val}"


def load_and_chunk_documents() -> List[Dict[str, Any]]:
    """
    Load all markdown files and split into chunks with metadata.
    
    Returns a list of chunk dicts with:
    - doc_id: unique deterministic identifier for the chunk
    - title: document title
    - source_path: original file path
    - collection: collection name
    - chunk_index: 0-based index within the document
    - content: the chunk text
    - metadata: dict with doc_id, title, source_path, collection, chunk_index
    """
    files = discover_markdown_files()
    chunks = []
    
    for file_info in files:
        try:
            with open(file_info["full_path"], "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_info['full_path']}: {e}")
            continue
        
        text_chunks = _split_into_chunks(content)
        
        for chunk_index, chunk_text in enumerate(text_chunks):
            doc_id = _generate_deterministic_id(
                file_info["collection"],
                file_info["relative_path"],
                chunk_index,
            )
            
            metadata = {
                "doc_id": doc_id,
                "title": file_info["title"],
                "source_path": file_info["relative_path"],
                "collection": file_info["collection"],
                "chunk_index": chunk_index,
            }
            
            chunks.append({
                "doc_id": doc_id,
                "content": chunk_text,
                "metadata": metadata,
            })
    
    return chunks


def get_collection_names() -> List[str]:
    """
    Get list of all collection names.
    
    Returns:
        List of collection names from COLLECTION_MAPPING values
    """
    return list(COLLECTION_MAPPING.values())
