"""Recommendation service - delegates to SHL pipeline (scraper, retrieval, GenAI)."""

import sys

from app.core.config import settings
from app.core.exceptions import RecommendationError

# Add SHL module to path so we can import pipeline
_shl_path = settings.shl_module_path
if str(_shl_path) not in sys.path:
    sys.path.insert(0, str(_shl_path))


class RecommendationService:
    """Business logic for recommendations. Uses existing SHL pipeline."""

    def recommend(
        self,
        query: str,
        top_k: int = 10,
        *,
        job_family: list[str] | None = None,
        job_level: list[str] | None = None,
        industry: list[str] | None = None,
        language: list[str] | None = None,
        job_category: list[str] | None = None,
    ) -> list[dict]:
        """
        Get SHL assessment recommendations for a job query.
        Delegates to existing pipeline (retrieval, reranker, GenAI query understanding).
        Supports SHL catalog filters: job_family, job_level, industry, language, job_category.
        """
        if not query or not query.strip():
            raise RecommendationError(
                message="Query cannot be empty",
                details=None,
            )

        try:
            # Import from SHL module - pipeline uses scraper, retrieval, reranker, GenAI
            from pipeline import recommend  # noqa: PLC0415

            use_llm = settings.use_llm
            results = recommend(
                query.strip(),
                top_k=top_k,
                min_recommendations=1,
                use_llm=use_llm,
                job_family=job_family,
                job_level=job_level,
                industry=industry,
                language=language,
                job_category=job_category,
            )
        except ImportError as e:
            raise RecommendationError(
                message="Recommendation pipeline not available. Ensure catalog and indices are built.",
                details={"import_error": str(e)},
            ) from e
        except Exception as e:
            raise RecommendationError(
                message=str(e),
                details=None,
            ) from e

        if not results:
            raise RecommendationError(
                message="No recommendations available. Build catalog and indices: python main.py build-from-train && python main.py build-indices",
                details=None,
            )

        return results
