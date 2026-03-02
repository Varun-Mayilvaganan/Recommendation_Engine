import type { RecommendRequest, RecommendResponse, ApiResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';

export async function getRecommendations(
  payload: RecommendRequest
): Promise<RecommendResponse['recommendations']> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: payload.query,
      top_k: payload.top_k ?? 10,
      ...(payload.job_family?.length && { job_family: payload.job_family }),
      ...(payload.job_level?.length && { job_level: payload.job_level }),
      ...(payload.industry?.length && { industry: payload.industry }),
      ...(payload.language?.length && { language: payload.language }),
      ...(payload.job_category?.length && { job_category: payload.job_category }),
    }),
    });
  } catch (e) {
    const msg =
      e instanceof TypeError && e.message === 'Failed to fetch'
        ? `Cannot reach the API at ${API_BASE}. Is the backend running? (python run.py on port 8080)`
        : e instanceof Error
          ? e.message
          : 'Network error';
    throw new Error(msg);
  }

  if (!res.ok) {
    const err = (await res.json()) as ApiResponse<unknown>;
    throw new Error(err.message ?? err.error ?? `HTTP ${res.status}`);
  }

  const data = (await res.json()) as ApiResponse<RecommendResponse>;
  const recommendations = data.data?.recommendations ?? (data as unknown as RecommendResponse).recommendations ?? [];
  return recommendations;
}
