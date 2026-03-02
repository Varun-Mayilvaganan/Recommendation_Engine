"""Stage 12: Weight tuning for fusion - grid search to improve Mean Recall@10."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from evaluation.runner import evaluate  # noqa: E402
from reranker.fusion import DEFAULT_WEIGHTS  # noqa: E402


def tune_weights() -> None:
    """
    Run evaluation with different fusion weights.
    Default: (0.4, 0.3, 0.2, 0.1) = dense, bm25, skill, seniority.
    """
    # We need to inject weights into the pipeline - for now we just run baseline
    # and print. Full grid search would require pipeline to accept weight param.
    print("Baseline weights:", DEFAULT_WEIGHTS)
    result = evaluate(top_k=10)
    print("\nBaseline Mean Recall@10:", result["mean_recall_at_10"])
    print("\nTo tune: modify reranker/fusion.py DEFAULT_WEIGHTS and re-run evaluate.")
