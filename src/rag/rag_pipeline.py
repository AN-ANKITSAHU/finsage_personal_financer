"""
RAG Pipeline — FinSage
Handles: embedding, ChromaDB setup, and retrieval.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from knowledge_base.documents import DOCUMENTS

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "finsage_kb"
TOP_K = 3


def load_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL_NAME)


def build_chromadb(embedder: SentenceTransformer) -> chromadb.Collection:
    client = chromadb.Client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [doc["id"] for doc in DOCUMENTS]
    texts = [doc["text"] for doc in DOCUMENTS]
    metadatas = [{"topic": doc["topic"]} for doc in DOCUMENTS]
    embeddings = embedder.encode(texts, convert_to_list=True)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"[RAG] Loaded {len(DOCUMENTS)} documents into ChromaDB.")
    return collection


def retrieve(
    question: str,
    embedder: SentenceTransformer,
    collection: chromadb.Collection,
    top_k: int = TOP_K,
) -> tuple[str, list[str]]:
    """
    Embed question, query ChromaDB, return (context_string, source_list).
    """
    query_embedding = embedder.encode([question], convert_to_list=True)[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context_parts = []
    sources = []
    for doc, meta in zip(docs, metas):
        topic = meta.get("topic", "Unknown")
        context_parts.append(f"[{topic}]\n{doc}")
        sources.append(topic)

    context_string = "\n\n---\n\n".join(context_parts)
    return context_string, sources
