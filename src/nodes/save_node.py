from src.state import FinanceState


def save_node(state: FinanceState) -> FinanceState:
    messages = list(state.get("messages", []))
    messages.append({"role": "assistant", "content": state["answer"]})
    return {**state, "messages": messages}
