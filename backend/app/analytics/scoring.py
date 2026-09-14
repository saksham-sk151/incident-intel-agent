"""
Recurrence / severity-weighted prioritization analytics.

This is the layer that reuses the statistics-driven approach from prior
analytics work: rather than just counting incidents per category, it
computes a severity-weighted score and a recency-weighted score, then
combines them into a single prioritization index -- and reports a
confidence signal (sample size per category) so small categories aren't
mistaken for stable, well-supported findings.
"""
import json
import math
from pathlib import Path

import pandas as pd

from app.core.config import DATA_DIR


def load_incidents_df() -> pd.DataFrame:
    path = DATA_DIR / "incidents.json"
    data = json.loads(path.read_text())
    return pd.DataFrame(data)


def compute_recurrence_priority(half_life_days: int = 180) -> list[dict]:
    """
    For each category, compute:
      - count: number of recorded incidents
      - mean_severity: average severity (1-5)
      - recency_weight: exponential decay so recent incidents count more
      - priority_score: normalized 0-100 score combining frequency,
        severity, and recency -- the metric used to rank prevention
        priorities, analogous to the "top-scoring segment" style finding
        from prior analytics work.
    """
    df = load_incidents_df()
    if df.empty:
        return []

    decay_lambda = math.log(2) / half_life_days
    df["recency_weight"] = df["days_ago"].apply(lambda d: math.exp(-decay_lambda * d))
    df["weighted_severity"] = df["severity"] * df["recency_weight"]

    grouped = df.groupby(["category", "category_label"]).agg(
        count=("id", "count"),
        mean_severity=("severity", "mean"),
        recency_weighted_severity=("weighted_severity", "sum"),
    ).reset_index()

    max_score = grouped["recency_weighted_severity"].max() or 1.0
    grouped["priority_score"] = (grouped["recency_weighted_severity"] / max_score * 100).round(1)
    grouped["mean_severity"] = grouped["mean_severity"].round(2)
    grouped["confidence"] = grouped["count"].apply(
        lambda n: "low" if n < 10 else ("medium" if n < 25 else "high")
    )

    grouped = grouped.sort_values("priority_score", ascending=False)
    return grouped.drop(columns=["recency_weighted_severity"]).to_dict(orient="records")


def compute_location_hotspots() -> list[dict]:
    df = load_incidents_df()
    if df.empty:
        return []
    grouped = df.groupby("location").agg(
        count=("id", "count"),
        mean_severity=("severity", "mean"),
    ).reset_index()
    grouped["mean_severity"] = grouped["mean_severity"].round(2)
    grouped = grouped.sort_values(["mean_severity", "count"], ascending=False)
    return grouped.to_dict(orient="records")
