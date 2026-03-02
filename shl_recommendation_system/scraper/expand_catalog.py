"""Expand catalog using train set URLs and crawl - supplements main scraper."""

import logging

import pandas as pd

from utils.config import DATASET_PATH

from .crawler import _session_with_retries, fetch_assessment_detail
from .parsers import extract_slug, normalize_url

logger = logging.getLogger(__name__)


def get_urls_from_train_set() -> list[str]:
    """Extract unique assessment URLs from train set."""
    if not DATASET_PATH.exists():
        return []
    try:
        df = pd.read_excel(DATASET_PATH, sheet_name="Train-Set")
        if "Assessment_url" in df.columns:
            urls = df["Assessment_url"].dropna().unique().tolist()
            return [str(u).strip() for u in urls if str(u).startswith("http")]
    except Exception as e:
        logger.warning("Could not read train set: %s", e)
    return []


def _make_stub_assessment(url: str, slug: str) -> dict:
    """Create minimal assessment record when fetch fails."""
    name = slug.replace("-", " ").title()
    return {
        "id": slug,
        "name": name,
        "url": url,
        "description": name,  # Use name as searchable text fallback
        "test_type": [],
        "duration": None,
        "job_level": [],
        "languages": [],
        "searchable_text": name,
    }


def expand_catalog_from_train(existing: list[dict]) -> list[dict]:
    """
    Add assessments from train set URLs that are not yet in catalog.
    Fetches each URL; if fetch fails, creates stub from URL/slug.
    """
    train_urls = get_urls_from_train_set()
    by_slug = {a["id"]: a for a in existing}
    session = _session_with_retries()

    for url in train_urls:
        slug = extract_slug(url)
        if not slug or slug in by_slug:
            continue
        # Use URL as-is; avoid double solutions in path
        if "/solutions/solutions/" in url:
            url = url.replace("/solutions/solutions/", "/solutions/")
        norm_url = normalize_url(url)
        detail = fetch_assessment_detail(session, norm_url, slug.replace("-", " ").title(), slug)
        if detail:
            by_slug[slug] = detail
            logger.info("Added from train set: %s", slug)
        else:
            # Stub so we have the assessment in catalog for retrieval
            by_slug[slug] = _make_stub_assessment(norm_url, slug)
            logger.info("Added stub from train set: %s", slug)

    return list(by_slug.values())
