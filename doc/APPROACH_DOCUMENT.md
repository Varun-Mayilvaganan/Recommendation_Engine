# SHL Assessment Recommendation System – Approach Document

## Problem Statement

Hiring managers and recruiters often struggle to find the right SHL assessments for a given job role. With 377+ Individual Test Solutions in the catalog, manual keyword search is both tedious and unreliable—it tends to miss good matches and over-rely on exact phrase matches. The goal was to build a system that accepts natural language job queries (or a job description URL), returns 5–10 relevant Individual Test Solutions, and supports catalog filters like job family, level, industry, language, and job category.

## Solution Overview

I built a hybrid retrieval pipeline that combines several techniques. First, an LLM (Gemini) parses the query to extract technical skills, soft skills, seniority, and domains. That structured output feeds into dense retrieval (FAISS with sentence-transformers) for semantic similarity and sparse retrieval (BM25) for lexical overlap. I then compute skill overlap scores against assessment metadata, fuse everything with tuned weights (0.4 dense, 0.3 BM25, 0.2 skill, 0.1 seniority), and apply balanced K/P selection so that when a query spans both technical and behavioral skills, we don't over-represent one type. Finally, MMR diversification reduces redundancy in the top results.

## Architecture

**Data pipeline.** The catalog is scraped via paginated HTTP requests to the SHL site (type=1 and type=2 with appropriate start offsets). When scraping is blocked or returns too little data, the catalog can be built from train-set URLs instead. Everything is stored as JSON; embeddings go into FAISS and BM25 indices are pickled. I use all-MiniLM-L6-v2 (384-dim) for dense retrieval.

**Retrieval flow.** Query → LLM query understanding → dense (top-50) + BM25 (top-50) → union of candidates → skill overlap scores → fusion → balanced K/P selection → MMR diversification → top-K.

**Application stack.** FastAPI backend on port 8080, React (Vite + TypeScript) frontend on 5173. The main endpoint is `POST /recommend` with filters; responses follow a standard `{data, message, error, error_code}` structure.

## Design Decisions

**Hybrid retrieval.** Dense embeddings capture semantic similarity (e.g., "collaboration" and "teamwork"), while BM25 preserves exact keyword matches (e.g., "Python", "SQL"). Skill overlap adds precision by using structured metadata like test_type and job_level.

**Balanced K/P selection.** Queries like "Java developer who collaborates" mix technical (K) and behavioral (P) skills. Without balancing, results skew heavily toward K-only assessments. I enforce at least 40% of each when both types are present in the query.

**MMR.** Maximal Marginal Relevance reduces redundancy—e.g., multiple nearly identical Java assessments—and improves diversity in the final list.

**LLM fallback.** When `GEMINI_API_KEY` is missing, a keyword-based fallback handles JavaScript vs Java disambiguation and basic skill extraction. Recall drops, but the system still runs.

## Optimization & Performance

Starting from a keyword-only baseline (no LLM), mean Recall@10 was around 0.35–0.38. Adding LLM query understanding improved skill extraction and overlap. I fixed the JavaScript vs Java ordering in the keyword fallback so "javascript" is checked before "java," which corrected some ranking issues. Balanced K/P and fusion tuning further improved results.

Final mean Recall@10 on the train set is 0.4133. Some per-query examples: Java developers + collaboration (0.60), Sales graduates (0.56), COO China (0.50), Senior Data Analyst SQL/Python (0.70), ICICI Admin (0.67).

## Catalog & Scraping

The primary approach is paginated HTTP GET to the SHL catalog (`?type=1&start=0,12,...,372` and `?type=2&start=0,12,...,132`). The parser extracts `/products/product-catalog/view/{slug}/` links and uses `data-course-id` and `data-entity-id` when available. If scraping returns insufficient data, the catalog is built from train-set URLs. The assignment expects at least 377 Individual Test Solutions; when scraping is limited, the train-set-derived catalog has 51 assessments. The pipeline is designed to scale when a full catalog is available.

## Submission Artifacts

- **submission.csv** – Test-set predictions (`Query`, `Assessment_url`, one row per query–URL pair), at project root and in `shl_recommendation_system/`
- **API** – `POST /recommend` with JSON request/response as described in the README
- **Frontend** – React app with query input, optional JD URL, and filters
- **Requirements mapping** – `doc/REQUIREMENTS.md` maps assignment requirements to the implementation

## How to Run

See the README for full setup. In short:

```bash
pip install -r requirements.txt
# Set GEMINI_API_KEY in .env

cd shl_recommendation_system
python main.py scrape          # or build-from-train
python main.py build-indices

python run.py                  # Backend at http://localhost:8080
cd frontend && npm run dev     # Frontend at http://localhost:5173

cd shl_recommendation_system
python main.py generate-submission
```

## References

- SHL Product Catalog: https://www.shl.com/solutions/products/product-catalog/
- Sentence-Transformers: all-MiniLM-L6-v2
- FAISS: Facebook AI Similarity Search
- BM25: Okapi BM25 via rank_bm25
