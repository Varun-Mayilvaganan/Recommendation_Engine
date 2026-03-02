"""Configuration and path utilities."""

from pathlib import Path

# Project root (parent of utils)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CATALOG_PATH = DATA_DIR / "shl_catalog.json"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index.bin"
FAISS_METADATA_PATH = DATA_DIR / "faiss_metadata.json"
BM25_INDEX_PATH = DATA_DIR / "bm25_index.pkl"
DATASET_PATH = PROJECT_ROOT.parent / "Gen_AI Dataset.xlsx"
SUBMISSION_PATH = PROJECT_ROOT / "submission.csv"


def ensure_data_dir() -> None:
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
