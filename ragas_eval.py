"""
ragas_eval.py — FinSage
Run with: python ragas_eval.py
Generates baseline faithfulness, answer_relevancy, context_precision scores.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
from src.rag.rag_pipeline import load_embedder, build_chromadb
from src.nodes.retrieval_node import init_retrieval
from src.graph import build_graph, ask

print("[RAGAS] Initialising agent...")
embedder = load_embedder()
collection = build_chromadb(embedder)
init_retrieval(embedder, collection)
app = build_graph()

# 5 eval pairs: question + ground truth from KB
EVAL_PAIRS = [
    {
        "question": "What is the 50/30/20 budgeting rule?",
        "ground_truth": "The 50/30/20 rule divides after-tax income into 50% for needs, 30% for wants, and 20% for savings and investments.",
    },
    {
        "question": "How much emergency fund should I have?",
        "ground_truth": "An emergency fund should cover 3 to 6 months of monthly expenses and should be kept in liquid instruments like a savings account or liquid mutual fund.",
    },
    {
        "question": "What is the PPF interest rate and lock-in period?",
        "ground_truth": "PPF offers 7.1% per annum interest, has a 15-year lock-in period, and provides EEE tax status — investment, interest, and maturity are all tax-free.",
    },
    {
        "question": "How is a credit score affected by credit utilisation?",
        "ground_truth": "Credit utilisation accounts for 30% of your credit score. You should use less than 30% of your credit card limit to maintain a good score.",
    },
    {
        "question": "What is term insurance and how much cover do I need?",
        "ground_truth": "Term insurance is pure life cover with no maturity benefit. You need 10 to 15 times your annual income as cover. A 25-year-old can get ₹1 crore cover for approximately ₹7,000–₹9,000 per year.",
    },
]

# Collect results
questions = []
answers = []
contexts = []
ground_truths = []

print("\n[RAGAS] Running agent on eval pairs...")
for i, pair in enumerate(EVAL_PAIRS, 1):
    result = ask(app, pair["question"], f"ragas_thread_{i:03d}")
    questions.append(pair["question"])
    answers.append(result.get("answer", ""))
    contexts.append([result.get("retrieved", "")])
    ground_truths.append(pair["ground_truth"])
    print(f"  [{i}/5] Done: {pair['question'][:60]}...")

# Try RAGAS evaluation
try:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    print("\n[RAGAS] Running evaluation metrics...")
    scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision])

    print("\n" + "="*50)
    print("RAGAS BASELINE SCORES")
    print("="*50)
    print(f"  Faithfulness       : {scores['faithfulness']:.4f}")
    print(f"  Answer Relevancy   : {scores['answer_relevancy']:.4f}")
    print(f"  Context Precision  : {scores['context_precision']:.4f}")
    print("="*50)
    print("Record these scores in your documentation.")

except ImportError:
    print("\n[RAGAS] ragas package not available. Running manual faithfulness check...")
    print("\n" + "="*50)
    print("MANUAL EVAL RESULTS")
    print("="*50)
    for i, (q, a, gt) in enumerate(zip(questions, answers, ground_truths), 1):
        print(f"\nQ{i}: {q}")
        print(f"  Answer   : {a[:200]}...")
        print(f"  GT       : {gt[:200]}")
        faith = float(result.get("faithfulness", 0.0)) if i == len(questions) else 0.0
        print(f"  LLM Faith: recorded during run")
    print("="*50)
