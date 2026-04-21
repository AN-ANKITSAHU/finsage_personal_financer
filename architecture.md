# Architecture — FinSage

## Full System Overview

```
User Input (Streamlit)
        │
        ▼
  [memory_node]       ← append to history, sliding window, extract name/income
        │
        ▼
  [router_node]       ← LLM classifies: retrieve | tool | memory_only
        │
   ┌────┴────────┐
   ▼             ▼
[retrieve]    [tool_node]    [skip_node]
   │             │               │
   └────┬────────┘───────────────┘
        ▼
  [answer_node]       ← LLM generates grounded answer
        │
        ▼
  [eval_node]         ← faithfulness check → retry if < 0.7
        │
        ▼
  [save_node]         ← append answer to history → END
        │
        ▼
   Streamlit UI
```

## Component Map

| Component       | Technology                        |
|-----------------|-----------------------------------|
| LLM             | groq/llama-3.1-8b-instant         |
| Embeddings      | all-MiniLM-L6-v2 (SentenceTransformers) |
| Vector DB       | ChromaDB (in-memory)              |
| Graph Framework | LangGraph (StateGraph)            |
| Memory          | MemorySaver + thread_id           |
| Tools           | Pure Python functions             |
| UI              | Streamlit                         |
| Evaluation      | LLM-based faithfulness (RAGAS-style) |

## Data Flow

1. User types question in Streamlit
2. Question + thread_id sent to LangGraph app.invoke()
3. memory_node adds to sliding window history
4. router_node classifies the query
5. Appropriate node runs (retrieve / tool / skip)
6. answer_node builds grounded response
7. eval_node checks faithfulness — retries once if below threshold
8. save_node persists answer to state
9. Streamlit displays final answer
