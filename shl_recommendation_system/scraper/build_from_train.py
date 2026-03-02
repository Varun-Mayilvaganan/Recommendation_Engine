"""Build catalog from train set URLs when scraping is blocked.

Use when the SHL site returns 405 or blocks requests.
Creates minimal assessment records from train set URLs.
Catalog is single source - no per-domain fallbacks.
"""

import json
import logging
from pathlib import Path

from utils.config import CATALOG_PATH, DATASET_PATH, ensure_data_dir

from .parsers import extract_slug, normalize_url

logger = logging.getLogger(__name__)


def build_catalog_from_train(output_path: Path | None = None) -> list[dict]:
    """Build catalog from train set Assessment_url column. No HTTP requests."""
    output_path = output_path or CATALOG_PATH
    ensure_data_dir()

    import pandas as pd  # noqa: PLC0415

    df = pd.read_excel(DATASET_PATH, sheet_name="Train-Set")
    urls = df["Assessment_url"].dropna().unique().tolist()

    assessments: list[dict] = []
    seen: set[str] = set()

    for url in urls:
        url = str(url).strip()
        if not url.startswith("http"):
            continue
        slug = extract_slug(url)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        norm_url = normalize_url(url)
        name = slug.replace("-", " ").replace("_", " ").title()
        assessments.append({
            "id": slug,
            "name": name,
            "url": norm_url,
            "description": name,
            "test_type": [],
            "duration": None,
            "job_level": [],
            "languages": [],
            "job_family": [],
            "industry": [],
            "job_category": [],
            "searchable_text": name,
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    logger.info("Built catalog from train set: %d assessments", len(assessments))
    print(f"Built catalog: {len(assessments)} assessments from train set -> {output_path}")
    return assessments
