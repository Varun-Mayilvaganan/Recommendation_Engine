"""Catalog loader - single source of truth. Load full catalog when ready."""

import json
from pathlib import Path
from typing import Any

from utils.config import CATALOG_PATH

# Catalog schema: id, name, url, description, test_type, duration,
# job_level, languages, job_family, industry, job_category, searchable_text


def load_catalog(path: Path | None = None) -> list[dict[str, Any]]:
    """
    Load catalog from JSON file. Single source - no fallbacks.
    Raises FileNotFoundError if catalog does not exist.
    """
    p = path or CATALOG_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Catalog not found at {p}. "
            "Build catalog first: python main.py scrape (or build-from-train)"
        )
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Catalog must be a JSON array of assessments")
    # Ensure all assessments have filter fields (backfill for older catalogs)
    for a in data:
        for field in ("job_family", "industry", "job_category"):
            if field not in a:
                a[field] = []
    return data


def catalog_ready(path: Path | None = None) -> bool:
    """Check if catalog exists and has assessments."""
    p = path or CATALOG_PATH
    if not p.exists():
        return False
    try:
        data = load_catalog(p)
        return len(data) > 0
    except Exception:
        return False


def ensure_catalog_fields(assessment: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure assessment has all filter fields. Backfill missing with empty lists.
    """
    for field in ("job_family", "industry", "job_category"):
        if field not in assessment:
            assessment[field] = []
    return assessment
