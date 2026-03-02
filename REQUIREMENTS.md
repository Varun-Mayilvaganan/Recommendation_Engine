# Assignment Requirements – Implementation Mapping

This document maps the **SHL AI Intern – Generative AI assignment** requirements to our implementation. Adjust section numbers and wording to match the exact PDF if needed.

---

## Requirement 1: Problem & Scope

| Requirement | Implementation |
|-------------|----------------|
| Accept natural language job query | `POST /recommend` accepts `query` (string); pipeline uses LLM + keyword fallback |
| Accept job description URL | Frontend supports optional JD URL; fetches HTML, extracts text, appends to query |
| Return 5–10 relevant assessments | `top_k` parameter (default 10, range 1–20); configurable per request |
| Individual Test Solutions only | Catalog scraper targets type=1 (Individual); filters exclude Pre-packaged when applicable |

---

## Requirement 2: Catalog

| Requirement | Implementation |
|-------------|----------------|
| ≥377 Individual Test Solutions | Paginated HTTP scraper (`type=1`, `start=0,12,...,372`); fallback: train-set build (51) when blocked |
| Catalog filters | `job_family`, `job_level`, `industry`, `language`, `job_category` in API request |
| Product URLs | Canonical format: `https://www.shl.com/solutions/products/product-catalog/view/{slug}/` |

---

## Requirement 3: API

| Requirement | Implementation |
|-------------|----------------|
| REST API | FastAPI backend; `POST /recommend` |
| Request format | `{"query": "...", "top_k": 10, "job_family": [...], ...}` |
| Response format | `{"data": {"recommendations": [{"assessment_name", "assessment_url", "score", "test_type"}]}, "message", "error", "error_code"}` |
| Health check | `GET /health` |

---

## Requirement 4: Frontend

| Requirement | Implementation |
|-------------|----------------|
| Query input | React textarea; placeholder for job query |
| Optional JD URL | Input field; fetches and merges text into query |
| Display 5–10 recommendations | Results list: name, score, test type, URL |
| Filters (optional) | Collapsible "Filters" section: Job Family, Level, Industry, Language, Job Category |

---

## Requirement 5: Submission

| Requirement | Implementation |
|-------------|----------------|
| submission.csv format | Columns: `Query`, `Assessment_url` |
| One row per query–URL pair | Up to 10 URLs per query; generated via `python main.py generate-submission` |
| Test set source | `Gen_AI Dataset.xlsx` sheet "Test-Set" |

---

## Requirement 6: Documentation

| Requirement | Implementation |
|-------------|----------------|
| README | Root `README.md`: setup, run, submission artifacts, API reference |
| Approach document | `APPROACH_DOCUMENT.md`: problem, solution, architecture, design decisions, performance |
| Requirements mapping | This file: `REQUIREMENTS.md` |

---

## Requirement 7: Evaluation (if applicable)

| Requirement | Implementation |
|-------------|----------------|
| Recall@K metric | `evaluation/recall.py`; `python main.py evaluate` |
| Train set | `Gen_AI Dataset.xlsx` sheet "Train-Set" |

---

## Checklist Before Submission

- [ ] `submission.csv` generated from Test-Set
- [ ] Backend runs: `python run.py` → http://localhost:8080
- [ ] Frontend runs: `cd frontend && npm run dev` → http://localhost:5173
- [ ] API returns valid JSON with `data.recommendations`
- [ ] README, APPROACH_DOCUMENT, REQUIREMENTS updated
- [ ] `.env.example` provided; no secrets in repo
