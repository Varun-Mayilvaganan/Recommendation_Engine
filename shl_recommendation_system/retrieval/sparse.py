"""BM25 sparse retrieval."""

import re
from pathlib import Path

from catalog.loader import load_catalog
from utils.config import BM25_INDEX_PATH, ensure_data_dir


def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, alphanumeric tokens."""
    text = (text or "").lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    return [t for t in tokens if len(t) > 1]


def build_index(index_path: Path | None = None) -> None:
    """Build BM25 index and save to pickle."""
    import pickle

    from rank_bm25 import BM25Okapi

    ensure_data_dir()
    index_path = index_path or BM25_INDEX_PATH
    catalog = load_catalog()
    texts = [_tokenize(a.get("searchable_text") or a.get("description") or a.get("name", "")) for a in catalog]
    bm25 = BM25Okapi(texts)
    data = {"bm25": bm25, "ids": [a["id"] for a in catalog]}
    with open(index_path, "wb") as f:
        pickle.dump(data, f)
    print(f"Built BM25 index: {len(catalog)} docs -> {index_path}")


def retrieve_bm25(
    query: str,
    top_k: int = 50,
    index_path: Path | None = None,
) -> list[dict]:
    """
    Retrieve top_k by BM25.
    Returns [{"id": ..., "score": ...}] with scores normalized to [0,1].
    """
    import pickle

    from rank_bm25 import BM25Okapi

    index_path = index_path or BM25_INDEX_PATH
    if not index_path.exists():
        build_index(index_path=index_path)

    with open(index_path, "rb") as f:
        data = pickle.load(f)
    bm25: BM25Okapi = data["bm25"]
    ids = data["ids"]

    tokens = _tokenize(query)
    scores = bm25.get_scores(tokens)
    top_indices = scores.argsort()[::-1][:top_k]

    raw = [float(scores[i]) for i in top_indices]
    min_s, max_s = min(raw), max(raw)
    if max_s - min_s > 1e-6:
        norm = [(s - min_s) / (max_s - min_s) for s in raw]
    else:
        norm = [1.0] * len(raw)

    return [{"id": ids[i], "score": norm[j]} for j, i in enumerate(top_indices)]
