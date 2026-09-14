"""
Regression test on retrieval quality: not a flaky exact-match test, but a
floor -- if a future change to tokenization, corpus, or ranking regresses
recall@5 below a reasonable floor, this test catches it. The floor (0.6) is
set below the currently-measured 0.8 so normal variation (e.g. adding more
synthetic incidents) doesn't make CI flaky, while still catching real
regressions.
"""
from app.rag.eval import evaluate


def test_recall_at_5_above_floor():
    report = evaluate(top_k_values=(1, 3, 5))
    assert report["recall_at_k"]["recall@5"] >= 0.6
    assert report["mrr"] >= 0.5


def test_every_eval_question_retrieves_something():
    report = evaluate(top_k_values=(5,))
    for q in report["per_question"]:
        assert len(q["retrieved_ids"]) == 5
