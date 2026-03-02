export interface RecommendationItem {
  assessment_name: string;
  assessment_url: string;
  score: number | null;
  test_type: string[];
}

export interface RecommendRequest {
  query: string;
  top_k?: number;
  job_family?: string[];
  job_level?: string[];
  industry?: string[];
  language?: string[];
  job_category?: string[];
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface RecommendResponse {
  recommendations: RecommendationItem[];
}
