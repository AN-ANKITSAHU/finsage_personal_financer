"""
graph.py — FinSage
Assembles the full LangGraph StateGraph.

Fix: renamed the registered node "answer" → "answer_node" to avoid a
LangGraph ≥0.2 validation error where a conditional edge mapping has the
same string as both a key and a node name ("answer": "answer"), which the
validator misreads as an edge from an unknown node.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import FinanceState
from src.nodes.memory_node import memory_node
from src.nodes.router_node import router_node
from src.nodes.retrieval_node import retrieval_node, skip_node
from src.nodes.tool_node import tool_node
from src.nodes.answer_node import answer_node
from src.nodes.eval_node import eval_node, eval_decision
from src.nodes.save_node import save_node


def route_decision(state: FinanceState) -> str:
    route = state.get("route", "retrieve")
    if route == "tool":
        return "tool"
    elif route == "memory_only":
        return "skip"
    return "retrieve"


def build_graph() -> any:
    graph = StateGraph(FinanceState)

    # Register all nodes
    # NOTE: registered as "answer_node" (not "answer") to avoid LangGraph
    # ≥0.2 collision between the node name and the conditional edge key.
    graph.add_node("memory",      memory_node)
    graph.add_node("router",      router_node)
    graph.add_node("retrieve",    retrieval_node)
    graph.add_node("tool",        tool_node)
    graph.add_node("skip",        skip_node)
    graph.add_node("answer_node", answer_node)   # ← renamed
    graph.add_node("eval",        eval_node)
    graph.add_node("save",        save_node)

    # Entry point
    graph.set_entry_point("memory")

    # Fixed edges
    graph.add_edge("memory",      "router")
    graph.add_edge("retrieve",    "answer_node")  # ← updated
    graph.add_edge("tool",        "answer_node")  # ← updated
    graph.add_edge("skip",        "answer_node")  # ← updated
    graph.add_edge("answer_node", "eval")         # ← updated
    graph.add_edge("save",        END)

    # Conditional: after router
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "retrieve": "retrieve",
            "tool":     "tool",
            "skip":     "skip",
        },
    )

    # Conditional: after eval
    # eval_decision() returns "answer_node" or "save"
    graph.add_conditional_edges(
        "eval",
        eval_decision,
        {
            "answer_node": "answer_node",  # ← updated
            "save":        "save",
        },
    )

    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)
    print("[Graph] Compiled successfully.")
    return app


def ask(app, question: str, thread_id: str, state_override: dict = None) -> dict:
    """Helper to invoke the graph and return full state."""
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "question":    question,
        "messages":    [],
        "route":       "",
        "retrieved":   "",
        "sources":     [],
        "tool_result": "",
        "answer":      "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name":   "",
        "income_info": "",
    }

    if state_override:
        initial_state.update(state_override)

    result = app.invoke(initial_state, config=config)
    return result
