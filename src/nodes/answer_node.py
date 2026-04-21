"""
answer_node.py — FinSage
Reads : question, retrieved, tool_result, messages, user_name, income_info, eval_retries
Writes: answer
"""

import os
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
            temperature=0.3,
        )
    return _llm


SYSTEM_PROMPT = """You are FinSage, a personal finance assistant for Indian salaried professionals.

RULES:
1. Answer ONLY using the provided context. Do not use outside knowledge.
2. If the context does not contain the answer, say exactly:
   "I don't have enough information in my knowledge base to answer this. Please consult a SEBI-registered financial advisor."
3. Never give specific investment advice (e.g., "buy this stock").
4. Never fabricate numbers, rates, or facts.
5. Keep answers clear, concise, and practical.
6. If a calculator result is provided, explain it in plain language.
{retry_instruction}

{user_context}"""

RETRY_INSTRUCTION = """
NOTE: Your previous answer was flagged for low faithfulness.
Use ONLY the context below. Do not add any information not present in the context."""


def answer_node(state: FinanceState) -> FinanceState:
    # Build user context string
    user_context_parts = []
    if state.get("user_name"):
        user_context_parts.append(f"User's name: {state['user_name']}")
    if state.get("income_info"):
        user_context_parts.append(f"User mentioned: {state['income_info']}")
    user_context = "\n".join(user_context_parts)

    retry_instr = RETRY_INSTRUCTION if state.get("eval_retries", 0) > 0 else ""

    system = SYSTEM_PROMPT.format(
        retry_instruction=retry_instr,
        user_context=user_context,
    ).strip()

    # Build context block
    if state.get("retrieved"):
        context_block = f"--- KNOWLEDGE BASE CONTEXT ---\n{state['retrieved']}\n"
    elif state.get("tool_result"):
        context_block = f"--- CALCULATOR RESULT ---\n{state['tool_result']}\n"
    else:
        context_block = "--- NO EXTERNAL CONTEXT AVAILABLE ---\n"

    # Build conversation history
    history_text = ""
    for msg in state.get("messages", [])[-6:]:
        role = msg.get("role", "")
        content = msg.get("content", "")
        history_text += f"{role.capitalize()}: {content}\n"

    full_prompt = (
        f"{system}\n\n"
        f"{context_block}\n"
        f"--- CONVERSATION HISTORY ---\n{history_text}\n"
        f"User: {state['question']}\n\n"
        f"Assistant:"
    )

    response = _get_llm().invoke(full_prompt)
    answer = response.content.strip()

    return {**state, "answer": answer}
