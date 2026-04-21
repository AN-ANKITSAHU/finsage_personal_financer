"""
memory_node — FinSage
Reads: question, messages
Writes: messages (updated), user_name, income_info
"""

import re
from src.state import FinanceState

WINDOW_SIZE = 6  # keep last 6 messages (3 turns)


def memory_node(state: FinanceState) -> FinanceState:
    question = state["question"]
    messages = list(state.get("messages", []))

    # Append current user question to history
    messages.append({"role": "user", "content": question})

    # Apply sliding window
    messages = messages[-WINDOW_SIZE:]

    # Extract user name if mentioned
    user_name = state.get("user_name", "")
    name_match = re.search(
        r"my name is ([A-Za-z]+)", question, re.IGNORECASE
    )
    if name_match:
        user_name = name_match.group(1).capitalize()

    # Extract income information if mentioned
    income_info = state.get("income_info", "")
    income_patterns = [
        r"(?:i earn|my salary is|my income is|i make|i get)\s+([\d,]+(?:\s*(?:k|lakh|lakhs|thousand|per month|/month|pm|pa|per annum|annually))*)",
        r"salary(?:\s+of)?\s+([\d,]+)",
    ]
    for pattern in income_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            income_info = f"User mentioned income: {match.group(0).strip()}"
            break

    return {
        **state,
        "messages": messages,
        "user_name": user_name,
        "income_info": income_info,
        "eval_retries": 0,  # reset for each new question
        "faithfulness": 0.0,
    }
