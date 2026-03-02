"""SHL catalog HTML parsers."""

import logging
import re
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Base URL for normalizing links
SHL_BASE = "https://www.shl.com"
VIEW_PATH_PATTERN = re.compile(r"/product-catalog/view/([^/]+)/?$", re.I)


def extract_slug(url: str) -> str | None:
    """Extract assessment slug from product catalog view URL."""
    if "/product-catalog/view/" not in url:
        return None
    match = VIEW_PATH_PATTERN.search(url)
    return match.group(1) if match else None


def normalize_url(url: str) -> str:
    """Normalize assessment URL to canonical form."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("/"):
        url = SHL_BASE + url
    # Use solutions path - only replace if not already there
    if "/solutions/products/product-catalog/" not in url:
        url = url.replace("/products/product-catalog/", "/solutions/products/product-catalog/")
    if not url.endswith("/"):
        url += "/"
    return url


def parse_catalog_page(html: str) -> list[dict[str, str]]:
    """
    Parse main catalog page and extract Individual Test Solutions links.
    Excludes Pre-packaged Job Solutions.
    Returns list of {name, url, test_type} from the Individual Test Solutions table.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find all tables
    tables = soup.find_all("table")
    individual_links: list[dict[str, str]] = []
    found_individual_header = False

    for table in tables:
        # Check if this is the Individual Test Solutions table
        first_row = table.find("tr")
        if first_row:
            first_cells = first_row.find_all(["th", "td"])
            first_text = " ".join(c.get_text(strip=True) for c in first_cells)

            if "Pre-packaged" in first_text and "Individual" not in first_text:
                continue  # Skip Pre-packaged table

            if "Individual Test Solutions" in first_text:
                found_individual_header = True
            elif found_individual_header:
                # We already processed Individual, skip any following tables
                break
            elif "Pre-packaged" in first_text:
                continue

        # Extract links from this table
        for link in table.find_all("a", href=True):
            href = link.get("href", "")
            if "/product-catalog/view/" not in href:
                continue

            # If we haven't found Individual table yet, this might be Pre-packaged - skip
            if not found_individual_header:
                continue

            slug = extract_slug(href)
            if not slug:
                continue

            full_url = normalize_url(href)
            name = link.get_text(strip=True) or slug.replace("-", " ").title()
            # Test type often in next cell - simplified: we'll get from detail page
            individual_links.append({"name": name, "url": full_url, "slug": slug})

    # Fallback: if no table structure, get all product-catalog/view links
    # and exclude known Pre-packaged slugs (from assignment context)
    if not individual_links:
        pre_packaged_slugs = {
            "account-manager-solution",
            "administrative-professional-short-form",
            "agency-manager-solution",
            "apprentice-8-0-job-focused-assessment",
            "apprentice-8-0-job-focused-assessment-4261",
            "bank-administrative-assistant-short-form",
            "bank-collections-agent-short-form",
            "bank-operations-supervisor-short-form",
            "bilingual-spanish-reservation-agent-solution",
            "bookkeeping-accounting-auditing-clerk-short-form",
            "branch-manager-short-form",
            "cashier-solution",
        }
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            slug = extract_slug(href)
            if slug and slug not in pre_packaged_slugs:
                full_url = normalize_url(href)
                name = link.get_text(strip=True) or slug.replace("-", " ").title()
                individual_links.append({"name": name, "url": full_url, "slug": slug})

    # Deduplicate by slug
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in individual_links:
        if item["slug"] not in seen:
            seen.add(item["slug"])
            unique.append(item)

    return unique


def parse_catalog_listing_page(html: str) -> list[dict[str, str]]:
    """
    Parse a single catalog listing page (paginated) and extract all product links.
    Looks for <a href="/products/product-catalog/view/{slug}/"> and optionally
    data-course-id, data-entity-id. Returns list of {name, url, slug, course_id?, entity_id?}.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: list[dict[str, str]] = []

    for link in soup.find_all("a", href=True):
        href = str(link.get("href") or "")
        if "/product-catalog/view/" not in href:
            continue
        slug = extract_slug(href)
        if not slug:
            continue
        full_url = normalize_url(href)
        name = link.get_text(strip=True) or slug.replace("-", " ").title()
        item: dict[str, str] = {"name": name, "url": full_url, "slug": slug}
        course_id = link.get("data-course-id")
        if course_id is not None:
            item["course_id"] = str(course_id)
        entity_id = link.get("data-entity-id")
        if entity_id is not None:
            item["entity_id"] = str(entity_id)
        links.append(item)

    # Deduplicate by slug (keep first)
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in links:
        if item["slug"] not in seen:
            seen.add(item["slug"])
            unique.append(item)

    return unique


def parse_assessment_detail(html: str, url: str, name: str, slug: str) -> dict[str, Any]:
    """
    Parse individual assessment detail page.
    Extracts description, test_type, duration, job_level, languages.
    """
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Any] = {
        "id": slug,
        "name": name,
        "url": url,
        "description": "",
        "test_type": [],  # List of K, P, S, A, B, E, D, C
        "duration": None,
        "job_level": [],
        "languages": [],
        "job_family": [],
        "industry": [],
        "job_category": [],
    }

    # Try to find description - common patterns (h4/h5 "Description" followed by content)
    for h in soup.find_all(["h4", "h5", "h6", "strong"]):
        if "description" in h.get_text(strip=True).lower():
            next_el = h.find_next_sibling()
            if next_el:
                result["description"] = next_el.get_text(strip=True)
            break

    # Fallback: first substantial paragraph
    if not result["description"]:
        for elem in soup.find_all(["p", "div"]):
            text = elem.get_text(strip=True)
            if len(text) > 50 and "select" not in text.lower() and "cookie" not in text.lower():
                result["description"] = text
                break

    # Job levels
    for elem in soup.find_all(string=re.compile(r"Job level", re.I)):
        parent = elem.parent
        if parent:
            next_el = parent.find_next_sibling()
            if next_el:
                levels = next_el.get_text(strip=True).split(",")
                result["job_level"] = [lev.strip() for lev in levels if lev.strip()]

    # Assessment length / duration
    pattern = re.compile(r"(?:Assessment length|Completion Time|minutes)", re.I)
    for elem in soup.find_all(string=pattern):
        text = elem if isinstance(elem, str) else elem.get_text()
        match = re.search(r"(\d+)\s*minutes?", text, re.I)
        if match:
            result["duration"] = int(match.group(1))
            break

    # Test Type (K, P, S, etc.)
    for elem in soup.find_all(string=re.compile(r"Test Type", re.I)):
        parent = elem.parent
        if parent:
            next_el = parent.find_next_sibling()
            if next_el:
                tt_text = next_el.get_text(strip=True)
                result["test_type"] = [c.strip() for c in tt_text if c.strip() in "KPSEABCD"]
            if not result["test_type"]:
                tt_text = parent.get_text(strip=True)
                result["test_type"] = [c for c in tt_text if c in "KPSEABCD"]

    # Languages
    for elem in soup.find_all(string=re.compile(r"Language", re.I)):
        parent = elem.parent
        if parent:
            next_el = parent.find_next_sibling()
            if next_el:
                result["languages"] = [
                    lang.strip()
                    for lang in next_el.get_text(strip=True).split(",")
                    if lang.strip()
                ]

    # Build searchable text
    result["searchable_text"] = " ".join(
        filter(
            None,
            [
                result["name"],
                result["description"],
                " ".join(result["test_type"]),
                " ".join(result["job_level"]),
            ],
        )
    ).strip()

    return result
