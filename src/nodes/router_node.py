"""
router_node.py — FinSage
Reads : state["question"], state["messages"]
Writes: state["route"]  →  "retrieve" | "tool" | "memory_only"
"""

import os
from dotenv import load_dotenv
from src.state import FinanceState

load_dotenv()  # ensures GROQ_API_KEY is available before ChatGroq is instantiated

from langchain_groq import ChatGroq  # noqa: E402

# Lazy singleton — created once on first import, not before .env is loaded
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


ROUTER_PROMPT = """You are a query router for a personal finance assistant.

Classify the user's question into EXACTLY one of these three categories:

- retrieve   : The question asks about a finance concept, definition, strategy,
               or policy (e.g., "what is SIP", "how does PPF work", "explain tax slabs").
               Answer requires fetching from a knowledge base.

- tool       : The question requires a calculation or real-time data
               (e.g., "calculate my EMI", "how much will ₹5000/month SIP give after 10 years",
               "what is today's date", "calculate compound interest").
               Answer requires running a function.

- memory_only: The question is a greeting, a follow-up using prior context,
               or small talk with no new information needed
               (e.g., "thanks", "what did you just say", "hi", "okay got it").

Reply with ONE WORD ONLY: retrieve, tool, or memory_only.
Do NOT explain. Do NOT add punctuation.

Conversation so far:
{history}

User question: {question}

Your classification:"""


def router_node(state: FinanceState) -> FinanceState:
    history_text = ""
    for msg in state.get("messages", [])[-4:]:
        role = msg.get("role", "")
        content = msg.get("content", "")
        history_text += f"{role}: {content}\n"

    prompt = ROUTER_PROMPT.format(
        history=history_text.strip() or "None",
        question=state["question"],
    )

    response = _get_llm().invoke(prompt)
    raw = response.content.strip().lower()

    if raw not in ("retrieve", "tool", "memory_only"):
        raw = "retrieve"

    return {**state, "route": raw}
