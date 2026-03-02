"""Main recommendation pipeline - orchestrates all stages."""

from typing import Any

from catalog.filters import apply_filters
from catalog.loader import load_catalog
from reranker.balance import balanced_select
from reranker.fusion import fuse_scores
from reranker.mmr import mmr_rerank
from reranker.query_understanding import understand_query
from reranker.skill_matching import compute_skill_scores
from retrieval.dense import retrieve_dense
from retrieval.sparse import retrieve_bm25


def recommend(
    query: str,
    top_k: int = 10,
    min_recommendations: int = 5,
    use_mmr: bool = True,
    llm_provider: str = "gemini",
    use_llm: bool | None = None,
    *,
    job_family: list[str] | None = None,
    job_level: list[str] | None = None,
    industry: list[str] | None = None,
    language: list[str] | None = None,
    job_category: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Full pipeline: query understanding -> dense + sparse + skill -> fuse -> balance -> MMR.
    Supports SHL filters: job_family, job_level, industry, language, job_category.
    Returns [{"assessment_name", "assessment_url", "score", "test_type"}].
    """
    if not query or not query.strip():
        return []

    import os

    use_llm = use_llm if use_llm is not None else bool(os.getenv("GEMINI_API_KEY"))

    # 0. Load catalog and apply filters
    catalog = load_catalog()
    filtered = apply_filters(
        catalog,
        job_family=job_family,
        job_level=job_level,
        industry=industry,
        language=language,
        job_category=job_category,
    )
    allowed_ids = {a["id"] for a in filtered} if filtered else {a["id"] for a in catalog}

    # 1. Query understanding
    qj = understand_query(query, provider=llm_provider, use_llm=use_llm)
    has_technical = bool(qj.get("technical_skills"))
    has_soft = bool(qj.get("soft_skills"))

    # 2. Retrieve (fetch more when filters applied to ensure enough after filtering)
    retrieve_k = 100 if allowed_ids != {a["id"] for a in catalog} else 50
    dense_results = retrieve_dense(query, top_k=retrieve_k)
    bm25_results = retrieve_bm25(query, top_k=retrieve_k)

    # Filter retrieval results by allowed_ids
    dense_results = [r for r in dense_results if r["id"] in allowed_ids]
    bm25_results = [r for r in bm25_results if r["id"] in allowed_ids]

    candidate_ids = {r["id"] for r in dense_results + bm25_results}
    if not candidate_ids:
        candidate_ids = allowed_ids

    # 3. Skill scores (for candidates only)
    skill_results = compute_skill_scores(qj, candidate_ids=candidate_ids)

    # 4. Fuse
    ranked = fuse_scores(dense_results, bm25_results, skill_results)

    # 5. Balanced select
    balanced = balanced_select(ranked, has_technical, has_soft, top_n=top_k)

    # 6. MMR diversify
    catalog = load_catalog()
    final = mmr_rerank(balanced, query, catalog=catalog, top_k=top_k)

    # 7. Format output
    by_id = {a["id"]: a for a in catalog}
    out = []
    for item in final[:max(min_recommendations, top_k)]:
        a = by_id.get(item["id"], {})
        out.append({
            "assessment_name": a.get("name", item["id"]),
            "assessment_url": a.get("url", ""),
            "score": round(item.get("score", 0), 4),
            "test_type": a.get("test_type", []),
        })

    return out
