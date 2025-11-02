"""
converting source data to embedding (vectors) -> Indexing (storing data in vector DB)
RAG operations
"""
from sentence_transformers import SentenceTransformer
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

#modular level
embedding_model = "BAAI/bge-small-en"
model = SentenceTransformer(embedding_model)
print("==========Embedding model loaded==============")

splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ".", ",", "!", "?", ""],
    chunk_size = 10,
    chunk_overlap = 2
)
print("========Splitter config loaded===========")

def chunking(data: str):
    parts = splitter.split_text(data)
    return parts

def convert_to_embedding(data: List[str]):
    encoded = model.encode(data)
    return encoded.tolist()