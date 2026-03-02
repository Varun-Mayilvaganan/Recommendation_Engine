"""Maximal Marginal Relevance for diversification."""

from typing import Any

# Use simple top-k by default to avoid loading model twice (dense already loads it)
USE_FULL_MMR = False


def mmr_rerank(
    items: list[dict[str, Any]],
    query: str,
    catalog: list[dict] | None = None,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    lambda_param: float = 0.6,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """
    MMR: balance relevance vs diversity.
    Uses simple top-by-score when USE_FULL_MMR=False to save memory.
    """
    if not items or top_k <= 0:
        return items[:top_k]
    if len(items) <= top_k or not USE_FULL_MMR:
        return items[:top_k]

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        by_id = {a["id"]: a for a in (catalog or [])}
        texts = [
            (by_id.get(i["id"], {})).get("searchable_text")
            or (by_id.get(i["id"], {})).get("name")
            or ""
            for i in items
        ]
        if not any(texts):
            return items[:top_k]
        embs = model.encode(texts, normalize_embeddings=True)
        selected: list[dict] = []
        remaining = list(items)
        id_to_emb = {items[j]["id"]: embs[j] for j in range(min(len(items), len(embs)))}

        for _ in range(top_k):
            if not remaining:
                break
            best_mmr = -1e9
            best_i = 0
            for i, cand in enumerate(remaining):
                rel = cand.get("score", 0.0)
                emb = id_to_emb.get(cand["id"])
                if emb is not None:
                    max_sim = 0.0
                    for s in selected:
                        se = id_to_emb.get(s["id"])
                        if se is not None:
                            sim = float(emb @ se)
                            max_sim = max(max_sim, sim)
                    mmr = lambda_param * rel - (1 - lambda_param) * max_sim
                else:
                    mmr = rel
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_i = i
            selected.append(remaining.pop(best_i))
        return selected
    except Exception:
        return items[:top_k]
