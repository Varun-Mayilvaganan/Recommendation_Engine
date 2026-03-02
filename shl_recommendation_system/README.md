# SHL Recommendation System – Core Pipeline

Catalog scraper, retrieval (FAISS + BM25), reranker, and evaluation. Used by the main app (`run.py`).

## Structure

```
shl_recommendation_system/
    data/           # Catalog, FAISS index, BM25 (generated)
    scraper/        # Catalog crawler
    retrieval/      # Dense + Sparse
    reranker/       # Fusion, balance, MMR
    evaluation/     # Recall@K, submission generator
    catalog/        # Loader, filters
    utils/          # Config, LLM client
    main.py         # CLI
```

## CLI Commands

```bash
python main.py build-from-train   # Build catalog from train set
python main.py scrape             # Scrape full catalog (paginated)
python main.py build-indices      # Build FAISS + BM25
python main.py generate-submission # Generate submission.csv
python main.py evaluate           # Recall@10 on train set
```

## Run Full App

From project root:
- Backend: `python run.py` (port 8080)
- Frontend: `cd frontend && npm run dev` (port 5173)
