"""Recommendation controller - API route handlers for SHL assessment recommendations."""

from fastapi import APIRouter, status

from app.core.exceptions import RecommendationError
from app.core.logger import log_api_entry, log_api_error, log_api_success
from app.schemas.recommendation import (
    RecommendRequest,
    RecommendationItem,
)
from app.services.recommendation_service import RecommendationService
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("")
async def recommend_assessments(payload: RecommendRequest) -> dict:
    """Get SHL assessment recommendations for a job query. Uses pipeline (GenAI, retrieval)."""
    endpoint = "POST /recommend"
    log_api_entry(endpoint, "POST", query_len=len(payload.query), top_k=payload.top_k)

    try:
        service = RecommendationService()
        results = service.recommend(
            query=payload.query,
            top_k=payload.top_k,
            job_family=payload.job_family or None,
            job_level=payload.job_level or None,
            industry=payload.industry or None,
            language=payload.language or None,
            job_category=payload.job_category or None,
        )
        recs = [
            RecommendationItem(
                assessment_name=r["assessment_name"],
                assessment_url=r["assessment_url"],
                score=r.get("score"),
                test_type=r.get("test_type", []),
            )
            for r in results
        ]
        log_api_success(endpoint, f"Returned {len(recs)} recommendations")
        return success_response(
            data={"recommendations": [r.model_dump() for r in recs]},
            message="Recommendations retrieved successfully",
        )
    except RecommendationError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to get recommendations",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
