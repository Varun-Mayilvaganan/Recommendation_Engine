"""Test case for DevOps engineer query.

Query: "We are looking for a DevOps engineer experienced in AWS, Docker, Kubernetes and CI/CD pipelines."
"""

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from pipeline import recommend

DEVOPS_QUERY = (
    "We are looking for a DevOps engineer experienced in AWS, Docker, Kubernetes "
    "and CI/CD pipelines."
)


def test_devops_query_returns_recommendations() -> None:
    """DevOps query should return non-empty recommendations."""
    results = recommend(DEVOPS_QUERY, top_k=10, use_llm=False)
    assert len(results) >= 1, "Should return at least 1 recommendation"
    assert len(results) <= 10, "Should return at most 10 recommendations"


def test_devops_query_result_structure() -> None:
    """Each recommendation must have assessment_name, assessment_url, score, test_type."""
    results = recommend(DEVOPS_QUERY, top_k=10, use_llm=False)
    for r in results:
        assert "assessment_name" in r
        assert "assessment_url" in r
        assert "score" in r
        assert "test_type" in r
        assert r["assessment_url"].startswith("https://")


def test_devops_query_with_llm() -> None:
    """DevOps query with LLM (if GEMINI_API_KEY set) should also return recommendations."""
    import os

    # Skip if no API key - LLM won't be used anyway
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set - skipping LLM test")

    results = recommend(DEVOPS_QUERY, top_k=10, use_llm=True)
    assert len(results) >= 1
    for r in results:
        assert "assessment_name" in r and "assessment_url" in r
