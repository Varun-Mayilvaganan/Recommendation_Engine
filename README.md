# Assessment Recommendation System

A production-grade recommendation system that suggests relevant SHL Individual Test Solutions given a natural language job query or job description URL.

---

## 1. Overview

| Item | Description |
|------|--------------|
| **Problem** | Hiring managers need relevant SHL assessments for job roles. Keyword search is inefficient. |
| **Solution** | Hybrid retrieval pipeline: LLM query understanding → Dense + Sparse retrieval → Skill matching → Fusion → Balanced K/P selection → MMR diversification |
| **Output** | 5–10 recommended assessments per query, with name, URL, score, and test type |

---

## 2. Project Structure

```
Recommendation_Engine/
├── app/                    # FastAPI backend (MVC)
│   ├── controllers/        # API routes
│   ├── services/           # Recommendation service
│   ├── schemas/            # Request/response models
│   └── main.py             # Application entry
├── shl_recommendation_system/   # Core pipeline
│   ├── scraper/            # Catalog crawler (paginated HTTP)
│   ├── retrieval/          # Dense (FAISS) + Sparse (BM25)
│   ├── reranker/           # Fusion, balance, MMR
│   ├── catalog/            # Loader, filters
│   ├── evaluation/         # Recall@K, submission generator
│   └── main.py             # CLI (scrape, build-indices, evaluate)
├── frontend/               # React (Vite + TypeScript)
├── run.py                  # Backend entry (port 8080)
├── requirements.txt
├── APPROACH_DOCUMENT.md     # Methodology & design decisions
├── REQUIREMENTS.md         # Assignment requirements mapping
└── submission.csv          # Test-set predictions (generated)
```

---

## 3. Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ (for React frontend)

### Backend

```bash
cd Recommendation_Engine
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate      # Linux/macOS

pip install -r requirements.txt
```

### Environment

Create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_key_here    # Required for LLM query understanding
DATABASE_URL=sqlite:///./recommendation_engine.db
APP_NAME=SHL Recommendation API
DEBUG=false
ENVIRONMENT=dev
```

### Catalog & Indices (one-time)

```bash
cd shl_recommendation_system

# Option A: Scrape full catalog (paginated HTTP)
python main.py scrape

# Option B: Build from train set only (when scraping blocked)
python main.py build-from-train

# Build FAISS + BM25 indices
python main.py build-indices
```

### Frontend

```bash
cd frontend
npm install
```

---

## 4. Run

### Backend (port 8080)

```bash
python run.py
```

API: http://localhost:8080  
Docs: http://localhost:8080/docs

### Frontend

```bash
cd frontend
npm run dev
```

UI: http://localhost:5173

---

## 5. Submission Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| **submission.csv** | Root & `shl_recommendation_system/submission.csv` | Test-set predictions: `Query`, `Assessment_url` |
| **API** | `POST /recommend` | Request: `{query, top_k?, job_family?, ...}` → `{data: {recommendations: [...]}}` |
| **Approach Document** | `APPROACH_DOCUMENT.md` | Methodology, architecture, optimization, limitations |
| **Requirements Mapping** | `REQUIREMENTS.md` | Assignment requirements → implementation mapping |
| **Submission Package** | `SUBMISSION_PACKAGE.md` | Checklist and file list for submission |

### Generate submission.csv

```bash
cd shl_recommendation_system
python main.py generate-submission
```

Output: `Query`, `Assessment_url` (one row per query–URL pair, up to 10 URLs per query). Also saved to root `submission.csv` for submission.

---

## 6. API Reference

### POST /recommend

**Request:**
```json
{
  "query": "Java developers with collaboration skills",
  "top_k": 10,
  "job_family": ["Information Technology"],
  "job_level": ["Mid-Professional"],
  "industry": [],
  "language": [],
  "job_category": []
}
```

**Response:**
```json
{
  "data": {
    "recommendations": [
      {
        "assessment_name": "Verify G+ Interactive",
        "assessment_url": "https://www.shl.com/solutions/products/product-catalog/view/verify-g-interactive/",
        "score": 0.823,
        "test_type": ["K", "P"]
      }
    ]
  },
  "message": "Recommendations retrieved successfully",
  "error": null,
  "error_code": null
}
```

---
