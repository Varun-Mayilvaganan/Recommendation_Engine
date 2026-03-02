"""Structured skill overlap and seniority matching."""

import json
from typing import Any

from utils.config import CATALOG_PATH


def _load_catalog() -> list[dict]:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _normalize(s: str) -> str:
    return (s or "").lower().strip()


def _overlap(query_terms: list[str], doc_text: str) -> float:
    """Jaccard-like overlap: |intersection| / |query_terms| if query non-empty else 0."""
    if not query_terms:
        return 0.0
    doc_lower = _normalize(doc_text)
    hits = sum(1 for t in query_terms if _normalize(t) in doc_lower)
    return hits / len(query_terms)


# Seniority level ordering for partial match
SENIORITY_ORDER = ["entry", "graduate", "mid-level", "professional", "senior", "manager", "executive"]


def _seniority_score(query_seniority: str, job_levels: list[str]) -> float:
    """Score 1 if exact/partial match, else partial."""
    q = _normalize(query_seniority)
    if q == "unknown" or not q:
        return 0.5  # Neutral
    levels_text = " ".join(job_levels).lower()
    if q in levels_text:
        return 1.0
    for s in ["entry", "graduate", "junior", "mid", "senior", "manager", "executive", "professional"]:
        if s in q and s in levels_text:
            return 0.8
    return 0.2


def compute_skill_scores(
    query_json: dict[str, Any],
    candidate_ids: set[str] | None = None,
) -> list[dict]:
    """
    Compute skill_overlap_score and seniority_score for each catalog assessment.
    candidate_ids: optional set to limit to these ids.
    Returns [{"id", "skill_overlap_score", "seniority_score"}].
    """
    catalog = _load_catalog()

    tech = query_json.get("technical_skills") or []
    soft = query_json.get("soft_skills") or []
    domains = query_json.get("domains") or []
    seniority = query_json.get("seniority") or "unknown"
    all_skills = tech + soft + domains

    results = []
    for a in catalog:
        aid = a.get("id", "")
        if candidate_ids and aid not in candidate_ids:
            continue
        text = " ".join(
            filter(
                None,
                [
                    a.get("searchable_text", ""),
                    a.get("description", ""),
                    a.get("name", ""),
                    " ".join(a.get("job_level", [])),
                ],
            )
        )
        skill_score = _overlap(all_skills, text) if all_skills else 0.5
        sen_score = _seniority_score(seniority, a.get("job_level", []))
        results.append({"id": aid, "skill_overlap_score": skill_score, "seniority_score": sen_score})

    return results
