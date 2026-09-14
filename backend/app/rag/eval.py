"""
Retrieval evaluation: computes recall@k and Mean Reciprocal Rank (MRR) on the
held-out question set in data/eval_questions.json, against the known-relevant
regulation IDs for each question.

Run: python -m app.rag.eval
Writes a JSON report to app/data/eval_report.json with real, reproducible
numbers -- not invented ones -- so every metric quoted in the README or a
resume bullet can be traced back to this script.
"""
import json

from app.core.config import DATA_DIR
from app.rag.retriever import get_retriever


def load_eval_set():
    return json.loads((DATA_DIR / "eval_questions.json").read_text())


def evaluate(top_k_values=(1, 3, 5)):
    retriever = get_retriever()
    eval_set = load_eval_set()

    results_per_k = {k: [] for k in top_k_values}
    reciprocal_ranks = []

    per_question_detail = []

    for item in eval_set:
        question = item["question"]
        relevant_ids = set(item["relevant_ids"])

        max_k = max(top_k_values)
        retrieved = retriever.retrieve(question, top_k=max_k)
        retrieved_ids = [r["doc_id"] for r in retrieved]

        # reciprocal rank of first relevant hit
        rr = 0.0
        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id in relevant_ids:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        hit_at_k = {}
        for k in top_k_values:
            hit = any(doc_id in relevant_ids for doc_id in retrieved_ids[:k])
            results_per_k[k].append(1.0 if hit else 0.0)
            hit_at_k[k] = hit

        per_question_detail.append({
            "question": question,
            "relevant_ids": list(relevant_ids),
            "retrieved_ids": retrieved_ids,
            "hit_at_k": hit_at_k,
            "reciprocal_rank": round(rr, 4),
        })

    recall_at_k = {f"recall@{k}": round(sum(v) / len(v), 4) for k, v in results_per_k.items()}
    mrr = round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4)

    report = {
        "n_questions": len(eval_set),
        "recall_at_k": recall_at_k,
        "mrr": mrr,
        "per_question": per_question_detail,
    }
    return report


if __name__ == "__main__":
    report = evaluate()
    out_path = DATA_DIR / "eval_report.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"n_questions = {report['n_questions']}")
    print(f"recall@k = {report['recall_at_k']}")
    print(f"MRR = {report['mrr']}")
    print(f"Full report written to {out_path}")
