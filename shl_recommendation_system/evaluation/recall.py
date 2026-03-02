"""Recall@K metrics."""


def recall_at_k(retrieved: list[str], relevant: set[str], k: int = 10) -> float:
    """Recall@K = |retrieved[:k] ∩ relevant| / |relevant|."""
    if not relevant:
        return 1.0
    top = retrieved[:k]
    hits = len(set(top) & relevant)
    return hits / len(relevant)


def mean_recall_at_k(
    results: list[tuple[list[str], set[str]]],
    k: int = 10,
) -> float:
    """Mean Recall@K over queries."""
    if not results:
        return 0.0
    return sum(recall_at_k(ret, rel, k) for ret, rel in results) / len(results)
