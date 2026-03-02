"""Catalog filter support - SHL filter dimensions (Job Family, Job Level, Industry, etc.)."""

from typing import Any

# SHL catalog filter options (from product catalog page)
JOB_FAMILIES = [
    "Business",
    "Clerical",
    "Contact Center",
    "Customer Service",
    "Information Technology",
    "Safety",
    "Sales",
]

JOB_LEVELS = [
    "Director",
    "Entry-Level",
    "Executive",
    "Front Line Manager",
    "General Population",
    "Graduate",
    "Manager",
    "Mid-Professional",
    "Professional Individual Contributor",
    "Supervisor",
]

INDUSTRIES = [
    "Banking/Finance",
    "Healthcare",
    "Hospitality",
    "Insurance",
    "Manufacturing",
    "Oil & Gas",
    "Retail",
    "Telecommunications",
]

# Common languages (subset; full list on SHL catalog)
LANGUAGES = [
    "English (USA)",
    "English (UK)",
    "English International",
    "Spanish",
    "French",
    "German",
    "Chinese Simplified",
    "Japanese",
    "Portuguese",
    "Portuguese (Brazil)",
]

JOB_CATEGORIES = [
    "Architecture and Engineering",
    "Arts, Design, and Media",
    "Building and Grounds Cleaning and Maintenance",
    "Business and Financial Operations",
    "Community and Social Services",
    "Computer and Mathematical",
    "Construction and Extraction",
    "Contact Center and Customer Service",
    "Education, Training, and Library",
    "Farming, Fishing, and Forestry",
    "Food Preparation and Serving Related",
    "Health and Environmental Science",
    "Healthcare Practitioners and Technical",
    "Healthcare Support",
    "Legal",
    "Management and Leadership",
    "Office and Administrative Support",
    "Personal Care and Service",
    "Production",
    "Protective Service",
    "Sales and Related",
    "Skilled Electrical, Mechanical, and Industrial",
    "Transportation and Material Moving",
]


def apply_filters(
    catalog: list[dict[str, Any]],
    *,
    job_family: list[str] | None = None,
    job_level: list[str] | None = None,
    industry: list[str] | None = None,
    language: list[str] | None = None,
    job_category: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Filter catalog by SHL dimensions.
    Each dimension: if provided, assessment must match at least one value (OR).
    Across dimensions: all provided filters must match (AND).
    """
    result = catalog
    filters_applied = False

    # Assessments with no value for a dimension pass through (match any)
    def _matches(dim_values: list[str], allowed: set[str]) -> bool:
        vals = set(dim_values or [])
        return not vals or bool(allowed & vals)

    if job_family:
        allowed = {f.strip() for f in job_family if f}
        if allowed:
            result = [a for a in result if _matches(a.get("job_family"), allowed)]
            filters_applied = True

    if job_level:
        allowed = {f.strip() for f in job_level if f}
        if allowed:
            result = [a for a in result if _matches(a.get("job_level"), allowed)]
            filters_applied = True

    if industry:
        allowed = {f.strip() for f in industry if f}
        if allowed:
            result = [a for a in result if _matches(a.get("industry"), allowed)]
            filters_applied = True

    if language:
        allowed = {f.strip().lower() for f in language if f}
        if allowed:
            result = [
                a
                for a in result
                if _matches(
                    [str(lang).lower() for lang in (a.get("languages") or [])],
                    allowed,
                )
            ]
            filters_applied = True

    if job_category:
        allowed = {f.strip() for f in job_category if f}
        if allowed:
            result = [a for a in result if _matches(a.get("job_category"), allowed)]
            filters_applied = True

    return result if filters_applied else catalog


def get_filter_options() -> dict[str, list[str]]:
    """Return all available filter options for API/UI."""
    return {
        "job_family": JOB_FAMILIES,
        "job_level": JOB_LEVELS,
        "industry": INDUSTRIES,
        "language": LANGUAGES,
        "job_category": JOB_CATEGORIES,
    }
