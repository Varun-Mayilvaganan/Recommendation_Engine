"""Balanced K/P selection - ensure mix when query has both technical and soft skills."""


from utils.config import CATALOG_PATH

K_TYPE = "K"  # Knowledge & Skills
P_TYPE = "P"  # Personality & Behavior
MIN_K_RATIO = 0.4
MIN_P_RATIO = 0.4


def _load_catalog() -> list[dict]:
    import json

    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _has_k(assessment: dict) -> bool:
    tt = assessment.get("test_type") or []
    if K_TYPE in tt or (isinstance(tt, str) and K_TYPE in tt):
        return True
    # Infer from name: technical/skill keywords -> K
    name = (assessment.get("name") or "").lower()
    desc = (assessment.get("description") or "").lower()
    text = name + " " + desc
    k_words = ["java", "python", "sql", "selenium", "javascript", "excel", "testing", "technical", "simulation"]
    return any(w in text for w in k_words)


def _has_p(assessment: dict) -> bool:
    tt = assessment.get("test_type") or []
    if P_TYPE in tt or (isinstance(tt, str) and P_TYPE in tt):
        return True
    # Infer from name: personality/behavior keywords -> P
    name = (assessment.get("name") or "").lower()
    desc = (assessment.get("description") or "").lower()
    text = name + " " + desc
    p_words = ["personality", "interpersonal", "communication", "leadership", "opq", "behavior", "motivation"]
    return any(w in text for w in p_words)


def balanced_select(
    ranked: list[dict],
    query_has_technical: bool,
    query_has_soft: bool,
    top_n: int = 10,
) -> list[dict]:
    """
    Select top_n with balance: if query has both technical+soft, ensure >=40% K and >=40% P.
    ranked: [{"id", "score", ...}] sorted by score.
    """
    catalog_by_id = {a["id"]: a for a in _load_catalog()}
    needs_balance = query_has_technical and query_has_soft
    if not needs_balance:
        return ranked[:top_n]

    min_k = max(1, int(top_n * MIN_K_RATIO))
    min_p = max(1, int(top_n * MIN_P_RATIO))
    selected: list[dict] = []
    k_count = 0
    p_count = 0

    for item in ranked:
        if len(selected) >= top_n:
            break
        a = catalog_by_id.get(item["id"], {})
        is_k = _has_k(a)
        is_p = _has_p(a)
        # Add if we need more K/P or if it fits
        if is_k and k_count < min_k:
            selected.append(item)
            k_count += 1
        elif is_p and p_count < min_p:
            selected.append(item)
            p_count += 1
        elif not is_k and not is_p:
            selected.append(item)
        # else skip if we already have enough K and P and this is K or P

    # Fill remaining with highest scores not yet selected
    selected_ids = {s["id"] for s in selected}
    for item in ranked:
        if len(selected) >= top_n:
            break
        if item["id"] not in selected_ids:
            selected.append(item)
            selected_ids.add(item["id"])

    return selected[:top_n]
