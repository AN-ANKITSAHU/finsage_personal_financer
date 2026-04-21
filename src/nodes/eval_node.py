"""
eval_node.py — FinSage
Reads : answer, retrieved, eval_retries
Writes: faithfulness (float), eval_retries (incremented)

Fix: eval_decision() now returns "answer_node" (not "answer") to match
the renamed node in graph.py, so the conditional edge resolves correctly.
"""

import os
import re
from dotenv import load_dotenv
from src.state import FinanceState

load_dotenv()

from langchain_groq import ChatGroq  # noqa: E402

_llm = None


def _get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ["GROQ_API_KEY"],
            temperature=0,
        )
    return _llm


EVAL_PROMPT = """You are a faithfulness evaluator for a finance AI assistant.

Your job: Score whether the ANSWER is grounded in the CONTEXT provided.

Scoring guide:
1.0 = Answer only uses information from the context. No outside claims.
0.8 = Answer mostly uses context, minor paraphrasing or common knowledge added.
0.6 = Answer partially uses context but adds some information not in context.
0.4 = Answer mostly ignores context and uses outside knowledge.
0.0 = Answer is completely unrelated to the context.

CONTEXT:
{context}

ANSWER:
{answer}

Reply with ONLY a decimal number between 0.0 and 1.0. Nothing else."""

MAX_RETRIES = 2
FAITHFULNESS_THRESHOLD = 0.7


def eval_node(state: FinanceState) -> FinanceState:
    # Skip evaluation if no retrieved context (tool answer — no KB to check against)
    if not state.get("retrieved", "").strip():
        return {
            **state,
            "faithfulness": 1.0,
            "eval_retries": state.get("eval_retries", 0),
        }

    prompt = EVAL_PROMPT.format(
        context=state["retrieved"][:3000],
        answer=state["answer"],
    )

    try:
        response = _get_llm().invoke(prompt)
        raw = response.content.strip()
        match = re.search(r"\d+\.?\d*", raw)
        score = float(match.group()) if match else 0.5
        score = max(0.0, min(1.0, score))
    except Exception:
        score = 0.5

    retries = state.get("eval_retries", 0)
    print(f"[EVAL] Faithfulness: {score:.2f} | Retries: {retries}")

    return {
        **state,
        "faithfulness": score,
        "eval_retries": retries + 1,
    }


def eval_decision(state: FinanceState) -> str:
    """
    Conditional edge after eval_node.
    Returns 'answer_node' to retry, or 'save' to proceed.
    Must match the node names registered in graph.py exactly.
    """
    score = state.get("faithfulness", 1.0)
    retries = state.get("eval_retries", 0)

    if score < FAITHFULNESS_THRESHOLD and retries <= MAX_RETRIES:
        print(f"[EVAL] Score {score:.2f} below threshold. Retrying answer_node.")
        return "answer_node"   # ← was "answer"
    return "save"
