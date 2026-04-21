# LangGraph Node Overview — FinSage

## Node List

| # | Node Name       | Input Fields                        | Output Fields                        | Role |
|---|-----------------|-------------------------------------|--------------------------------------|------|
| 1 | memory_node     | question, messages                  | messages, user_name, income_info     | Append question to history, extract user context |
| 2 | router_node     | question, messages                  | route                                | Classify query: retrieve / tool / memory_only |
| 3 | retrieval_node  | question                            | retrieved, sources                   | Embed query, fetch top-3 ChromaDB chunks |
| 4 | tool_node       | question                            | tool_result                          | Run calculator / datetime function |
| 5 | skip_node       | —                                   | retrieved="", sources=[]             | No-op passthrough for memory_only route |
| 6 | answer_node     | question, retrieved, tool_result, messages, user_name, income_info | answer | Build grounded LLM response |
| 7 | eval_node       | answer, retrieved, eval_retries     | faithfulness, eval_retries           | Score faithfulness; retry if < 0.7 |
| 8 | save_node       | answer, messages                    | messages                             | Append answer to history → END |

## Conditional Edges

### After router_node
```
route == "retrieve"    → retrieval_node
route == "tool"        → tool_node
route == "memory_only" → skip_node
```

### After eval_node
```
faithfulness >= 0.7 OR eval_retries >= 2  → save_node
faithfulness < 0.7  AND eval_retries < 2  → answer_node (retry)
```

## Fixed Edges
```
memory_node     → router_node
retrieval_node  → answer_node
tool_node       → answer_node
skip_node       → answer_node
answer_node     → eval_node
save_node       → END
```
