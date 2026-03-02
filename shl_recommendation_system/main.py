"""SHL Assessment Recommendation System - CLI entry."""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def cmd_build_indices() -> None:
    """Build FAISS and BM25 indices from catalog."""
    from catalog.loader import catalog_ready

    if not catalog_ready():
        raise SystemExit(
            "Catalog not found. Build catalog first: "
            "python main.py scrape (or build-from-train)"
        )
    from retrieval.dense import build_index
    from retrieval.sparse import build_index as build_bm25

    build_index()
    build_bm25()
    print("Indices built.")


def cmd_prepare() -> None:
    """Load catalog and build indices - single flow when catalog is ready."""
    from catalog.loader import catalog_ready

    if not catalog_ready():
        print("Catalog not found. Run: python main.py build-from-train")
        print("(Or: python main.py scrape for full catalog)")
        raise SystemExit(1)
    cmd_build_indices()
    print("Application ready. Run: python run.py (backend) and cd frontend && npm run dev (React UI)")


def cmd_scrape() -> None:
    """Scrape SHL catalog."""
    from scraper.crawler import crawl

    crawl()
    print("Scraping complete.")


def cmd_build_from_train() -> None:
    """Build catalog from train set only (when scraping blocked)."""
    from scraper.build_from_train import build_catalog_from_train

    build_catalog_from_train()
    print("Catalog built from train set.")


def cmd_evaluate() -> None:
    """Run evaluation on train set."""
    from evaluation.runner import evaluate

    evaluate()


def cmd_generate_submission() -> None:
    """Generate submission.csv."""
    from evaluation.generate_submission import generate

    generate()


def main() -> None:
    parser = argparse.ArgumentParser(description="SHL Recommendation System")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-indices", help="Build FAISS and BM25 indices from catalog")
    sub.add_parser("prepare", help="Build indices when catalog ready (catalog + indices)")
    sub.add_parser("scrape", help="Scrape SHL catalog")
    sub.add_parser("build-from-train", help="Build catalog from train set only")
    sub.add_parser("evaluate", help="Run Recall@10 evaluation")
    sub.add_parser("generate-submission", help="Generate submission.csv")
    sub.add_parser("tune", help="Run weight tuning evaluation")

    args = parser.parse_args()
    if args.cmd == "build-indices":
        cmd_build_indices()
    elif args.cmd == "prepare":
        cmd_prepare()
    elif args.cmd == "scrape":
        cmd_scrape()
    elif args.cmd == "build-from-train":
        cmd_build_from_train()
    elif args.cmd == "evaluate":
        cmd_evaluate()
    elif args.cmd == "generate-submission":
        cmd_generate_submission()
    elif args.cmd == "tune":
        from evaluation.tune_weights import tune_weights

        tune_weights()


if __name__ == "__main__":
    main()
