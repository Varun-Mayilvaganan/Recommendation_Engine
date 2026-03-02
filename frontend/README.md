# SHL Assessment Recommendation – React frontend

Single-page UI for the recommendation API. No sidebar; filters are optional in the main content.

## Setup

```bash
npm install
```

Optional: copy `.env.example` to `.env` and set `VITE_API_URL` if the backend is not at `http://localhost:8000`.

## Run

With the FastAPI backend running (e.g. `python run.py` from project root):

```bash
npm run dev
```

Open http://localhost:5173 (or the port Vite prints).

## Build

```bash
npm run build
```

Output is in `dist/`. Serve with any static host or `npm run preview`.
