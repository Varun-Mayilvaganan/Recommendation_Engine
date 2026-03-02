"""SHL catalog crawler - fetches full catalog via paginated HTTP (Individual + Pre-packaged)."""

import json
import logging
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.config import CATALOG_PATH, ensure_data_dir

from .parsers import (
    normalize_url,
    parse_assessment_detail,
    parse_catalog_listing_page,
    parse_catalog_page,
)

logger = logging.getLogger(__name__)

CATALOG_BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
# Pagination: type=1 (Individual) start=0,12,...,372; type=2 (Pre-packaged) start=0,12,...,132
TYPE1_STARTS = list(range(0, 373, 12))   # 0, 12, ..., 372
TYPE2_STARTS = list(range(0, 133, 12))   # 0, 12, ..., 132
MIN_ASSESSMENTS = 377
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0
REQUEST_DELAY = 0.5  # Be respectful to the server


def _session_with_retries() -> requests.Session:
    """Create requests session with retry logic."""
    session = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def fetch_catalog_links(session: requests.Session) -> list[dict[str, str]]:
    """
    Fetch all catalog product links via paginated HTTP GET.
    Paginates type=1 (start=0,12,...,372) and type=2 (start=0,12,...,132),
    parses each page for /products/product-catalog/view/{slug}/ links, dedupes by slug.
    """
    all_links: list[dict[str, str]] = []
    seen_slugs: set[str] = set()
    total_pages = len(TYPE1_STARTS) + len(TYPE2_STARTS)
    page_num = 0

    print("Fetching catalog listing pages (type=1 + type=2)...")
    for catalog_type, starts in [(1, TYPE1_STARTS), (2, TYPE2_STARTS)]:
        for start in starts:
            page_num += 1
            url = f"{CATALOG_BASE_URL}?type={catalog_type}&start={start}"
            try:
                resp = session.get(url, timeout=30)
                resp.raise_for_status()
                page_links = parse_catalog_listing_page(resp.text)
                for item in page_links:
                    if item["slug"] not in seen_slugs:
                        seen_slugs.add(item["slug"])
                        all_links.append(item)
                print(f"  Listing page {page_num}/{total_pages} (type={catalog_type}, start={start}) -> {len(all_links)} links so far")
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", url, e)
                print(f"  Warning: page {page_num}/{total_pages} failed: {e}")

    print(f"Listing done: {len(all_links)} catalog product links.")
    logger.info("Parsed %d catalog product links from paginated listing", len(all_links))

    # Fallback: single main page if pagination returned nothing
    if not all_links:
        logger.info("Pagination returned no links; trying main catalog page.")
        resp = session.get(CATALOG_BASE_URL, timeout=30)
        resp.raise_for_status()
        all_links = parse_catalog_page(resp.text)
        logger.info("Parsed %d links from main catalog page", len(all_links))

    if not all_links:
        try:
            from .browser import extract_individual_links_with_playwright

            playwright_links = extract_individual_links_with_playwright()
            if playwright_links:
                all_links = playwright_links
                logger.info("Playwright fallback fetched %d links", len(all_links))
        except Exception as e:
            logger.warning("Playwright fallback failed: %s", e)

    return all_links


def fetch_assessment_detail(
    session: requests.Session, url: str, name: str, slug: str
) -> dict | None:
    """Fetch and parse a single assessment detail page."""
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        return parse_assessment_detail(resp.text, url, name, slug)
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return None


def _expand_from_train_set(assessments: list[dict]) -> list[dict]:
    """Merge in assessments from train set URLs not yet in catalog."""
    try:
        from .expand_catalog import expand_catalog_from_train

        return expand_catalog_from_train(assessments)
    except Exception as e:
        logger.warning("Train set expansion failed: %s", e)
        return assessments


def crawl(output_path: Path | None = None) -> list[dict]:
    """
    Crawl full SHL catalog (both Individual and Pre-packaged) via paginated HTTP
    and return list of assessments. Falls back to main page or train-set if needed.
    """
    output_path = output_path or CATALOG_PATH
    ensure_data_dir()

    try:
        session = _session_with_retries()
        links = fetch_catalog_links(session)
    except Exception as e:
        logger.warning("Catalog fetch failed (%s). Building from train set only.", e)
        from .build_from_train import build_catalog_from_train

        return build_catalog_from_train(output_path)

    if len(links) < MIN_ASSESSMENTS:
        logger.warning(
            "Only %d catalog links found (expected more from pagination). Continuing.",
            len(links),
        )

    assessments: list[dict] = []
    seen_slugs: set[str] = set()
    total_links = len(links)
    progress_interval = max(1, total_links // 20)  # print ~20 times during detail fetch

    print(f"Fetching detail pages for {total_links} products...")
    for i, item in enumerate(links):
        slug = item["slug"]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        url = item.get("url") or normalize_url(f"https://www.shl.com/solutions/products/product-catalog/view/{slug}/")
        name = item.get("name", slug.replace("-", " ").title())

        detail = fetch_assessment_detail(session, url, name, slug)
        if detail:
            assessments.append(detail)
            n = len(assessments)
            if n % progress_interval == 0 or n == total_links:
                print(f"  Fetched {n}/{total_links}: {name[:50]}{'...' if len(name) > 50 else ''}")
            logger.debug("Fetched %d/%d: %s", n, total_links, name)

        time.sleep(REQUEST_DELAY)

    # Deduplicate by slug (prefer last/fullest)
    by_slug: dict[str, dict] = {}
    for a in assessments:
        by_slug[a["id"]] = a
    assessments = list(by_slug.values())

    # Expand from train set URLs to increase coverage
    if len(assessments) < MIN_ASSESSMENTS:
        assessments = _expand_from_train_set(assessments)
        by_slug = {a["id"]: a for a in assessments}
        assessments = list(by_slug.values())

    # Validate count
    total = len(assessments)
    print(f"Total catalog products scraped: {total}")
    if total < MIN_ASSESSMENTS:
        logger.warning(
            "Scraped %d assessments (expected >= %d from pagination).",
            total,
            MIN_ASSESSMENTS,
        )
    if total < 10:
        raise ValueError(
            f"Scraped {total} assessments; catalog fetch may have failed."
        )

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    logger.info("Saved %d assessments to %s", total, output_path)
    return assessments


def main() -> None:
    """CLI entry for scraper."""
    logging.basicConfig(level=logging.INFO)
    crawl()
    print("Scraping complete.")


if __name__ == "__main__":
    main()
