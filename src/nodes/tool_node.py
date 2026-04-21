from src.state import FinanceState
from src.tools.finance_tools import dispatch_tool


def tool_node(state: FinanceState) -> FinanceState:
    result = dispatch_tool(state["question"])
    return {**state, "tool_result": result, "retrieved": "", "sources": []}
