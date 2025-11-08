"""
Vector Database Indexing Module
Handles storage and retrieval of document embeddings using FAISS.

This module implements RAG (Retrieval Augmented Generation) by:
1. Storing document chunks with their embeddings
2. Retrieving relevant chunks based on query similarity
3. Providing context to AI models for accurate answers
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple

# ========================================
# FAISS Index Configuration
# ========================================
DIMENSION = 384  # Dimension for BAAI/bge-small-en model
INDEX_PATH = "faiss_index.bin"  # Path to save FAISS index
CHUNKS_PATH = "chunks_data.pkl"  # Path to save chunk metadata

# Initialize FAISS index (L2 distance)
index = faiss.IndexFlatL2(DIMENSION)

# Storage for document chunks and metadata
chunks_storage = []

# Load existing index if available
if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
    try:
        index = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_PATH, "rb") as f:
            chunks_storage = pickle.load(f)
        print(f"✅ Loaded existing index with {index.ntotal} vectors")
    except Exception as e:
        print(f"⚠️ Could not load existing index: {e}")
        print("Starting with fresh index")
else:
    print("🆕 Created new FAISS index")


# ========================================
# Storage Functions
# ========================================
def store_embeddings(
    chunks: List[str],
    embeddings: List[List[float]],
    metadata: Dict = None
) -> bool:
    """
    Store document chunks and their embeddings in FAISS index.
    
    Args:
        chunks: List of text chunks from the document
        embeddings: List of embedding vectors (one per chunk)
        metadata: Optional metadata (e.g., filename, upload_date, user_id)
        
    Returns:
        bool: True if storage successful
        
    Example:
        chunks = ["Chapter 1 text...", "Chapter 2 text..."]
        embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
        store_embeddings(chunks, embeddings, {"filename": "book.pdf"})
    """
    try:
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add embeddings to FAISS index
        index.add(embeddings_array)
        
        # Store chunks with metadata
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "chunk_index": len(chunks_storage) + i,
                "text_length": len(chunk)
            }
            # Add custom metadata if provided
            if metadata:
                chunk_data.update(metadata)
            chunks_storage.append(chunk_data)
        
        # Save index and chunks to disk
        faiss.write_index(index, INDEX_PATH)
        with open(CHUNKS_PATH, "wb") as f:
            pickle.dump(chunks_storage, f)
        
        print(f"✅ Stored {len(chunks)} chunks in FAISS index (Total: {index.ntotal})")
        return True
        
    except Exception as e:
        print(f"❌ Error storing embeddings: {e}")
        return False


# ========================================
# Retrieval Functions
# ========================================
def search_similar_chunks(
    query_embedding: List[float],
    top_k: int = 3
) -> Dict:
    """
    Find most similar document chunks to a query.
    
    Uses L2 distance to find chunks most relevant to the query.
    These chunks provide context for the AI model to answer questions.
    
    Args:
        query_embedding: Embedding vector of the user's question
        top_k: Number of most similar chunks to return (default: 3)
        
    Returns:
        Dict containing:
            - documents: List of matching text chunks
            - metadatas: Metadata for each chunk
            - distances: Similarity scores (lower = more similar)
            
    Example:
        from utils.ai_utils import model
        query_emb = model.encode("What is Chapter 1 about?")
        results = search_similar_chunks(query_emb.tolist(), top_k=3)
        context = "\n\n".join(results["documents"])
    """
    try:
        if index.ntotal == 0:
            print("⚠️ No documents in index")
            return {"documents": [], "metadatas": [], "distances": []}
        
        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS index
        # D = distances (lower is more similar), I = indices
        top_k = min(top_k, index.ntotal)  # Don't search for more than available
        distances, indices = index.search(query_array, top_k)
        
        # Extract results
        documents = []
        metadatas = []
        distances_list = distances[0].tolist()
        
        for idx in indices[0]:
            if idx < len(chunks_storage):
                chunk_data = chunks_storage[idx]
                documents.append(chunk_data["text"])
                metadatas.append({k: v for k, v in chunk_data.items() if k != "text"})
        
        print(f"🔍 Found {len(documents)} relevant chunks")
        
        return {
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances_list
        }
        
    except Exception as e:
        print(f"❌ Error searching chunks: {e}")
        return {"documents": [], "metadatas": [], "distances": []}


def get_context_for_query(query_text: str, embedding_model, top_k: int = 3) -> str:
    """
    Get relevant context from stored documents for a query.
    
    This is the main RAG function that:
    1. Converts query to embedding
    2. Searches for similar chunks
    3. Returns formatted context string
    
    Args:
        query_text: User's question
        embedding_model: SentenceTransformer model for encoding
        top_k: Number of chunks to retrieve
        
    Returns:
        str: Formatted context from relevant document chunks
        
    Example:
        from utils.ai_utils import model
        context = get_context_for_query("What is FastAPI?", model)
        # Returns: "Context from documents:\n\n1. FastAPI is..."
    """
    # Convert query to embedding
    query_embedding = embedding_model.encode(query_text).tolist()
    
    # Search for similar chunks
    results = search_similar_chunks(query_embedding, top_k)

    print(results)
    
    # Format context
    if not results["documents"]:
        return "No relevant context found in uploaded documents."
    
    context_parts = []
    for i, doc in enumerate(results["documents"], 1):
        context_parts.append(f"{i}. {doc}")
    
    context = "Context from documents:\n\n" + "\n\n".join(context_parts)
    return context


# ========================================
# Utility Functions
# ========================================
def clear_all_documents():
    """
    Clear all documents from the FAISS index.
    Use with caution - this deletes all stored data!
    """
    try:
        global index, chunks_storage
        index = faiss.IndexFlatL2(DIMENSION)
        chunks_storage = []
        
        # Remove saved files
        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)
        if os.path.exists(CHUNKS_PATH):
            os.remove(CHUNKS_PATH)
        
        print("🗑️ All documents cleared from FAISS index")
        return True
    except Exception as e:
        print(f"❌ Error clearing index: {e}")
        return False


def get_collection_stats() -> Dict:
    """
    Get statistics about stored documents.
    
    Returns:
        Dict with count of stored chunks
    """
    try:
        return {
            "total_chunks": index.ntotal,
            "dimension": DIMENSION
        }
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return {"total_chunks": 0, "dimension": DIMENSION}


# ========================================
# Module Initialization
# ========================================
print(f"==========FAISS Vector DB initialized (dimension: {DIMENSION})==============")
