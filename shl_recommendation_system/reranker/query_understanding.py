"""Query understanding via LLM - extract structured skills, seniority, domains."""

from typing import Any

from utils.llm_client import complete, extract_json_from_response

QUERY_PROMPT = """Analyze this job query or job description and extract structured information.
Return ONLY a valid JSON object with these exact keys (no other text):
{{
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "seniority": "entry|mid-level|senior|executive|graduate|manager|unknown",
  "domains": ["domain1", "domain2"]
}}

Rules:
- technical_skills: languages, tools (e.g., Java, Python, SQL, JavaScript, Selenium). JS != Java.
- soft_skills: behavioral traits (e.g., collaboration, communication, leadership)
- seniority: infer from "senior", "junior", "entry-level", "graduate", "manager", "executive", "COO", etc.
- domains: job area (e.g., development, sales, marketing, QA, data analysis)

Query:
{query}
"""


def _keyword_fallback(query: str) -> dict[str, Any]:
    """Simple keyword extraction when LLM unavailable. No domain-specific fallbacks."""
    q = query.lower()
    tech = []
    domains = []
    # Check "javascript" / "java script" before "java" to avoid matching Core Java when user wants JS
    if "javascript" in q or "java script" in q:
        tech.append("Javascript")
    elif "java" in q:
        tech.append("Java")
    for s in ["python", "sql", "selenium", "excel", "tableau"]:
        if s in q:
            tech.append(s.title())
    soft = []
    for s in ["collaborat", "communicat", "leadership", "teamwork"]:
        if s in q:
            soft.append(s.title())
    seniority = "unknown"
    if "senior" in q or "executive" in q or "coo" in q:
        seniority = "senior"
    elif "entry" in q or "graduate" in q or "junior" in q:
        seniority = "entry"
    elif "mid" in q or "manager" in q:
        seniority = "mid-level"
    return {"technical_skills": tech, "soft_skills": soft, "seniority": seniority, "domains": domains}


def understand_query(query: str, provider: str = "gemini", use_llm: bool = True) -> dict[str, Any]:
    """
    Extract structured JSON from natural language query.
    Returns dict with technical_skills, soft_skills, seniority, domains.
    Falls back to keyword extraction if LLM fails.
    """
    if not query or not query.strip():
        return {"technical_skills": [], "soft_skills": [], "seniority": "unknown", "domains": []}

    if not use_llm:
        return _keyword_fallback(query)
    prompt = QUERY_PROMPT.format(query=query[:4000])
    try:
        raw = complete(prompt, provider=provider)
    except Exception:
        return _keyword_fallback(query)

    parsed = extract_json_from_response(raw)
    if not parsed:
        return _keyword_fallback(query)

    return {
        "technical_skills": list(parsed.get("technical_skills") or []),
        "soft_skills": list(parsed.get("soft_skills") or []),
        "seniority": str(parsed.get("seniority") or "unknown").lower(),
        "domains": list(parsed.get("domains") or []),
    }
