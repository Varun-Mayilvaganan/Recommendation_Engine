"""Dense retrieval with sentence-transformers and FAISS."""

from pathlib import Path

from catalog.loader import load_catalog as _load_catalog
from utils.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH, ensure_data_dir


def build_index(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    index_path: Path | None = None,
    metadata_path: Path | None = None,
) -> None:
    """Build FAISS index from catalog. Save index and metadata."""
    import json

    import faiss
    from sentence_transformers import SentenceTransformer

    ensure_data_dir()
    index_path = index_path or FAISS_INDEX_PATH
    metadata_path = metadata_path or FAISS_METADATA_PATH

    catalog = _load_catalog()  # from catalog.loader
    if not catalog:
        raise ValueError("Catalog is empty")

    model = SentenceTransformer(model_name)
    texts = [a.get("searchable_text") or a.get("description") or a.get("name", "") for a in catalog]
    embeddings = model.encode(texts, normalize_embeddings=True)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype("float32"))

    faiss.write_index(index, str(index_path))
    meta = [{"id": a["id"], "name": a["name"], "url": a["url"], "test_type": a.get("test_type", [])} for a in catalog]
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    print(f"Built FAISS index: {len(catalog)} docs -> {index_path}")


_MODEL_CACHE: dict = {}


def _get_model(model_name: str):
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]


def retrieve_dense(
    query: str,
    top_k: int = 50,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    index_path: Path | None = None,
    metadata_path: Path | None = None,
) -> list[dict]:
    """
    Retrieve top_k by dense similarity.
    Returns [{"id": ..., "score": ...}] with scores normalized to [0,1].
    """
    import json

    import faiss

    index_path = index_path or FAISS_INDEX_PATH
    metadata_path = metadata_path or FAISS_METADATA_PATH
    if not index_path.exists():
        build_index(model_name=model_name, index_path=index_path, metadata_path=metadata_path)

    model = _get_model(model_name)
    q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
    index = faiss.read_index(str(index_path))
    scores, indices = index.search(q_emb, min(top_k, index.ntotal))

    with open(metadata_path, encoding="utf-8") as f:
        meta = json.load(f)

    # Normalize scores to [0,1] (cosine similarity from IP can be -1 to 1, typically 0-1)
    raw = scores[0]
    min_s, max_s = raw.min(), raw.max()
    if max_s - min_s > 1e-6:
        norm = (raw - min_s) / (max_s - min_s)
    else:
        norm = raw * 0 + 1.0

    return [
        {"id": meta[int(idx)]["id"], "score": float(norm[r])}
        for r, idx in enumerate(indices[0])
    ]
