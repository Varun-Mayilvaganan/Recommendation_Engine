# SHL Recommendation API - MVC Backend

FastAPI backend following strict MVC architecture with integrated SHL recommendation pipeline (scraper, retrieval, GenAI).

## Structure

```
app/
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic request/response
├── controllers/  # API route handlers
├── services/     # Business logic (calls pipeline, repositories)
├── repositories/ # Database CRUD
├── core/         # config, logger, database, exceptions
├── utils/        # response builder
└── main.py       # Entrypoint
```

## Run

```bash
# From project root
cd d:\My_Projects\Recommendation_Engine
pip install -r requirements.txt

# Build catalog & indices (first time)
cd shl_recommendation_system
python main.py build-from-train
python main.py build-indices
cd ..

# Start API
python run.py
# or: uvicorn app.main:app --reload
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Endpoints

- `GET /health` - Health check
- `GET /` - Root info
- `POST /users` - Create user
- `GET /users` - List users
- `GET /users/{id}` - Get user
- `PATCH /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user
- `POST /recommend` - SHL assessment recommendations (uses pipeline)

## Response Format

All endpoints return:

```json
{
  "data": <payload>,
  "message": "Success message",
  "error": null,
  "error_code": null
}
```

## Frontend Compatibility

The Streamlit frontend at `shl_recommendation_system/frontend/app.py` uses the API when "Use local pipeline" is unchecked. The new API returns `{ data: { recommendations: [...] } }`. Update the frontend to use `response.json().get("data", {}).get("recommendations", [])` when calling this API.
