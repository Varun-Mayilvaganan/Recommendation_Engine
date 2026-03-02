"""Tests for recall metrics."""

from evaluation.recall import mean_recall_at_k, recall_at_k


def test_recall_at_k_empty_relevant() -> None:
    assert recall_at_k(["a", "b"], set(), k=10) == 1.0


def test_recall_at_k_full_hit() -> None:
    assert recall_at_k(["a", "b", "c"], {"a", "b", "c"}, k=10) == 1.0


def test_recall_at_k_partial() -> None:
    assert recall_at_k(["a", "b", "x"], {"a", "b", "c"}, k=10) == 2 / 3


def test_mean_recall() -> None:
    results = [
        (["a", "b"], {"a", "b"}),
        (["x"], {"a", "b"}),
    ]
    assert mean_recall_at_k(results, k=10) == 0.5
