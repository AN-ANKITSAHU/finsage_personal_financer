# finsage/src/rag/__init__.py
# RAG sub-package.
# Exposes the three public functions used across the project:
#
#   from src.rag import load_embedder, build_chromadb, retrieve
#
from src.rag.rag_pipeline import load_embedder, build_chromadb, retrieve

__all__ = ["load_embedder", "build_chromadb", "retrieve"]
