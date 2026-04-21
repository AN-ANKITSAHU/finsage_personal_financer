# Success Criteria — FinSage

## Minimum (Pass)
- All 6 mandatory capabilities present and functional
- Runs end-to-end without errors
- Streamlit UI loads and accepts input
- Knowledge base has 10+ documents loaded into ChromaDB
- Multi-turn conversation works (context retained across 3+ turns)

## Good
- Router correctly classifies retrieve / tool / memory_only on 8/10 test questions
- Out-of-scope questions return a clear refusal, not a hallucinated answer
- Faithfulness score > 0.75 on RAGAS evaluation
- Red-team tests documented with PASS/FAIL

## Excellent
- Before/after RAGAS scores showing improvement after prompt tuning
- Calculator tool handles SIP, EMI, compound interest, tax bracket
- Streaming responses in the Streamlit UI
- Written reflection on limitations included in documentation
- income_info and user_name extracted and reused across turns
