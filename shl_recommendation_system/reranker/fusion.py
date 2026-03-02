"""Score fusion and hybrid ranking."""

# Default weights per plan: 0.4 dense, 0.3 bm25, 0.2 skill, 0.1 seniority
DEFAULT_WEIGHTS = (0.4, 0.3, 0.2, 0.1)


def fuse_scores(
    dense: list[dict],
    bm25: list[dict],
    skill: list[dict],
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> list[dict]:
    """
    Fuse scores: w0*dense + w1*bm25 + w2*skill_overlap + w3*seniority.
    Each input: [{"id", "score", ...}]. skill has skill_overlap_score, seniority_score.
    """
    w_d, w_b, w_s, w_sen = weights
    by_id: dict[str, dict] = {}

    def add(id_: str, d: float, b: float, sk: float, sen: float):
        fused = w_d * d + w_b * b + w_s * sk + w_sen * sen
        by_id[id_] = {"id": id_, "score": fused, "dense": d, "bm25": b, "skill": sk, "seniority": sen}

    for item in dense:
        by_id[item["id"]] = {
            "id": item["id"], "score": 0.0, "dense": item["score"],
            "bm25": 0.0, "skill": 0.0, "seniority": 0.0,
        }
    for item in bm25:
        if item["id"] in by_id:
            by_id[item["id"]]["bm25"] = item["score"]
        else:
            by_id[item["id"]] = {
                "id": item["id"], "score": 0.0, "dense": 0.0,
                "bm25": item["score"], "skill": 0.0, "seniority": 0.0,
            }
    skill_by_id = {s["id"]: s for s in skill}
    for id_, v in by_id.items():
        sk_item = skill_by_id.get(id_, {})
        sk = sk_item.get("skill_overlap_score", 0.0)
        sen = sk_item.get("seniority_score", 0.0)
        v["skill"] = sk
        v["seniority"] = sen
        v["score"] = w_d * v["dense"] + w_b * v["bm25"] + w_s * sk + w_sen * sen

    ranked = sorted(by_id.values(), key=lambda x: -x["score"])
    return ranked
