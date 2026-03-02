"""Generate submission.csv for test set."""

import csv
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd  # noqa: E402

from pipeline import recommend  # noqa: E402
from utils.config import DATASET_PATH, PROJECT_ROOT, SUBMISSION_PATH  # noqa: E402


def generate() -> Path:
    """Generate submission.csv from test set."""
    df = pd.read_excel(DATASET_PATH, sheet_name="Test-Set")
    rows = []
    for _, row in df.iterrows():
        query = str(row["Query"]).strip()
        recs = recommend(
            query,
            top_k=10,
            min_recommendations=5,
            use_llm=bool(__import__("os").getenv("GEMINI_API_KEY")),
        )
        for r in recs:
            rows.append({"Query": query, "Assessment_url": r["assessment_url"]})

    with open(SUBMISSION_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Assessment_url"])
        writer.writeheader()
        writer.writerows(rows)

    # Also copy to project root for submission
    root_submission = PROJECT_ROOT.parent / "submission.csv"
    if root_submission != SUBMISSION_PATH:
        import shutil
        shutil.copy(SUBMISSION_PATH, root_submission)
        print(f"Also saved to {root_submission}")

    print(f"Saved submission to {SUBMISSION_PATH}")
    return SUBMISSION_PATH
