"""
retrieval_node — FinSage
Reads: state["question"]
Writes: state["retrieved"], state["sources"]
"""

from src.state import FinanceState
from src.rag.rag_pipeline import retrieve


# These are injected at app startup from main.py / streamlit app
_embedder = None
_collection = None


def init_retrieval(embedder, collection):
    global _embedder, _collection
    _embedder = embedder
    _collection = collection


def retrieval_node(state: FinanceState) -> FinanceState:
    if _embedder is None or _collection is None:
        raise RuntimeError("retrieval_node: embedder/collection not initialised. Call init_retrieval() first.")

    context_string, sources = retrieve(
        question=state["question"],
        embedder=_embedder,
        collection=_collection,
    )

    return {
        **state,
        "retrieved": context_string,
        "sources": sources,
    }


def skip_node(state: FinanceState) -> FinanceState:
    """No-op passthrough for memory_only route."""
    return {
        **state,
        "retrieved": "",
        "sources": [],
        "tool_result": "",
    }
