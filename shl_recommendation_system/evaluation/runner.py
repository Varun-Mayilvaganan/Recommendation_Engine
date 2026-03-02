"""Evaluation runner - load dataset, run pipeline, compute Recall@10."""

# Add project root for imports
import sys
from pathlib import Path

import pandas as pd

from pipeline import recommend

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluation.recall import mean_recall_at_k, recall_at_k  # noqa: E402
from utils.config import DATASET_PATH  # noqa: E402


def _normalize_url(u: str) -> str:
    u = str(u).strip()
    u = u.replace("/solutions/solutions/", "/solutions/")
    u = u.replace("/products/product-catalog/", "/solutions/products/product-catalog/")
    if u.endswith("/"):
        return u[:-1]
    return u


def evaluate(top_k: int = 10) -> dict:
    """
    Run evaluation on train set. Returns dict with per-query recall and mean.
    """
    df = pd.read_excel(DATASET_PATH, sheet_name="Train-Set")
    # Group by query, collect relevant URLs
    query_to_relevant: dict[str, set[str]] = {}
    for _, row in df.iterrows():
        q = str(row["Query"]).strip()
        url = _normalize_url(row["Assessment_url"])
        if q not in query_to_relevant:
            query_to_relevant[q] = set()
        query_to_relevant[q].add(url)

    results = []
    per_query = []
    for query, relevant in query_to_relevant.items():
        recs = recommend(query, top_k=top_k, use_llm=False)  # Use keyword fallback for eval speed
        retrieved_urls = [_normalize_url(r["assessment_url"]) for r in recs]
        r10 = recall_at_k(retrieved_urls, relevant, k=top_k)
        per_query.append((query[:60] + "...", r10))
        results.append((retrieved_urls, relevant))

    mean_r10 = mean_recall_at_k(results, k=top_k)
    print("Per-query Recall@10:")
    for q, r in per_query:
        print(f"  {r:.4f}  {q}")
    print(f"\nMean Recall@10: {mean_r10:.4f}")

    return {
        "mean_recall_at_10": mean_r10,
        "per_query": [{"query": q, "recall_at_10": r} for q, r in per_query],
    }
