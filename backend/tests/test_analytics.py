from app.analytics.scoring import compute_recurrence_priority, compute_location_hotspots


def test_recurrence_priority_structure():
    rows = compute_recurrence_priority()
    assert len(rows) == 6
    for row in rows:
        assert 0 <= row["priority_score"] <= 100
        assert row["confidence"] in ("low", "medium", "high")
        assert row["count"] > 0


def test_recurrence_priority_is_sorted_descending():
    rows = compute_recurrence_priority()
    scores = [r["priority_score"] for r in rows]
    assert scores == sorted(scores, reverse=True)


def test_higher_half_life_changes_ranking_inputs():
    # A much shorter half-life should weight recent incidents far more heavily
    # than a long one -- the two settings should not always produce identical
    # scores (sanity check that recency weighting is actually doing something).
    short = {r["category"]: r["priority_score"] for r in compute_recurrence_priority(half_life_days=30)}
    long = {r["category"]: r["priority_score"] for r in compute_recurrence_priority(half_life_days=3650)}
    assert short != long


def test_hotspots_structure():
    rows = compute_location_hotspots()
    assert len(rows) == 6  # 6 locations in the synthetic dataset
    for row in rows:
        assert row["count"] > 0
