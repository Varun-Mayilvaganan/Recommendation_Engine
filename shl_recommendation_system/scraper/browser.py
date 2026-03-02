"""Playwright-based catalog fetcher for JS-rendered pages."""

import logging
import re
import time

logger = logging.getLogger(__name__)

VIEW_PATH_PATTERN = re.compile(r"/product-catalog/view/([^/]+)/?$", re.I)

# Slugs from Pre-packaged Job Solutions table (from catalog structure)
PRE_PACKAGED_SLUGS = {
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


def extract_individual_links_with_playwright() -> list[dict[str, str]]:
    """
    Use Playwright to render the catalog page and extract Individual Test Solutions.
    Excludes Pre-packaged Job Solutions by slug.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")

    links: list[dict[str, str]] = []
    seen_slugs: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.shl.com/solutions/products/product-catalog/", wait_until="networkidle")
        time.sleep(4)

        # Scroll to trigger lazy loading
        for _ in range(8):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.8)

        # Get ALL product-catalog/view links from page, exclude Pre-packaged
        anchors = page.locator("a[href*='/product-catalog/view/']").all()
        for a in anchors:
            href = a.get_attribute("href") or ""
            m = VIEW_PATH_PATTERN.search(href)
            if m:
                slug = m.group(1)
                if slug in seen_slugs or slug in PRE_PACKAGED_SLUGS:
                    continue
                seen_slugs.add(slug)
                try:
                    name = a.inner_text().strip() or slug.replace("-", " ").title()
                except Exception:
                    name = slug.replace("-", " ").title()
                url = href if href.startswith("http") else "https://www.shl.com" + href
                url = url.replace("/products/product-catalog/", "/solutions/products/product-catalog/")
                if not url.endswith("/"):
                    url += "/"
                links.append({"name": name, "url": url, "slug": slug})

        browser.close()

    return links
