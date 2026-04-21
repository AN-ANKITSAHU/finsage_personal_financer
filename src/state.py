from typing import TypedDict, List, Optional


class FinanceState(TypedDict):
    # ── Core ──────────────────────────────────────────────
    question: str
    # The user's current question for this turn.

    messages: List[dict]
    # Full conversation history as list of {"role": ..., "content": ...}.
    # Sliding window applied in memory_node (keeps last 6).

    route: str
    # Routing decision: "retrieve" | "tool" | "memory_only"
    # Written by router_node, read by conditional edge.

    # ── RAG ───────────────────────────────────────────────
    retrieved: str
    # Formatted context string from ChromaDB top-3 chunks.
    # Example: "[Budgeting] 50/30/20 rule means..."

    sources: List[str]
    # List of document topic names returned by retrieval.
    # Used in answer_node to cite sources.

    # ── Tool ──────────────────────────────────────────────
    tool_result: str
    # Output string from the calculator or datetime tool.
    # Empty string if route != "tool".

    # ── Answer ────────────────────────────────────────────
    answer: str
    # Final LLM-generated response shown to the user.

    # ── Evaluation ────────────────────────────────────────
    faithfulness: float
    # Score 0.0–1.0: does the answer stay within retrieved context?
    # Below 0.7 triggers a retry via eval_node.

    eval_retries: int
    # Safety counter. Max 2 retries to prevent infinite loops.

    # ── Domain-Specific (Finance) ─────────────────────────
    user_name: Optional[str]
    # Extracted if user says "my name is ...".
    # Reused in answer_node for personalisation.

    income_info: Optional[str]
    # Extracted if user mentions salary/income (e.g., "I earn ₹60,000/month").
    # Prepended to answer_node system prompt for context-aware responses.
