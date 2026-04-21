"""
capstone_streamlit.py — FinSage
Run with: streamlit run capstone_streamlit.py
"""

import streamlit as st
import uuid
import os

st.set_page_config(
    page_title="FinSage — Personal Finance AI",
    page_icon="💰",
    layout="wide",
)


@st.cache_resource
def load_agent():
    from sentence_transformers import SentenceTransformer
    from src.rag.rag_pipeline import load_embedder, build_chromadb
    from src.nodes.retrieval_node import init_retrieval
    from src.graph import build_graph

    embedder = load_embedder()
    collection = build_chromadb(embedder)
    init_retrieval(embedder, collection)
    app = build_graph()
    return app


app = load_agent()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 FinSage")
    st.caption("Personal Finance Agentic AI")
    st.markdown("---")
    st.markdown("**Topics I can help with:**")
    topics = [
        "📊 Budgeting (50/30/20 rule)",
        "🆘 Emergency Fund",
        "📈 SIP & Mutual Funds",
        "🏦 PPF & Tax Saving",
        "🧾 Income Tax Slabs",
        "🏠 Home Loan EMI",
        "💳 Credit Score / CIBIL",
        "🛡️ Term Insurance",
        "📉 Stock Market Basics",
        "🧮 Finance Calculations",
    ]
    for t in topics:
        st.markdown(f"- {t}")
    st.markdown("---")
    st.caption("⚠️ Not financial advice. For personalised guidance, consult a SEBI-registered advisor.")
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_meta = {}
        st.rerun()

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "last_meta" not in st.session_state:
    st.session_state.last_meta = {}

# ── Main Layout ───────────────────────────────────────────────────────────────
col_chat, col_meta = st.columns([3, 1])

with col_chat:
    st.title("FinSage 💰")
    st.caption("Ask me anything about personal finance — budgeting, SIP, EMI, tax, insurance, credit scores.")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about SIP, tax slabs, EMI, budgeting..."):
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                from src.graph import ask as graph_ask

                # Pass existing messages so memory persists
                result = graph_ask(
                    app=app,
                    question=prompt,
                    thread_id=st.session_state.thread_id,
                    state_override={"messages": st.session_state.messages.copy()},
                )

                answer = result.get("answer", "Sorry, I could not generate a response.")
                st.markdown(answer)

                # Update session state
                st.session_state.messages = result.get("messages", [])
                st.session_state.last_meta = {
                    "route": result.get("route", "—"),
                    "sources": result.get("sources", []),
                    "faithfulness": result.get("faithfulness", 0.0),
                    "eval_retries": result.get("eval_retries", 0),
                }

with col_meta:
    st.markdown("### 🔍 Agent Trace")
    meta = st.session_state.last_meta

    if meta:
        route = meta.get("route", "—")
        route_color = {"retrieve": "🟢", "tool": "🟠", "memory_only": "🔵"}.get(route, "⚪")
        st.metric("Route", f"{route_color} {route}")

        faith = meta.get("faithfulness", 0.0)
        faith_label = "✅ Pass" if faith >= 0.7 else "⚠️ Low"
        st.metric("Faithfulness", f"{faith:.2f} {faith_label}")

        retries = meta.get("eval_retries", 0)
        st.metric("Eval Retries", retries)

        sources = meta.get("sources", [])
        if sources:
            st.markdown("**Sources retrieved:**")
            for s in sources:
                st.markdown(f"- {s}")
    else:
        st.info("Ask a question to see agent trace here.")

    st.markdown("---")
    st.markdown("**Session ID**")
    st.code(st.session_state.thread_id[:16] + "...", language=None)
