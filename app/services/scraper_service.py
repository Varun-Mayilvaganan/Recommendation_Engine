"""Scraper service - delegates to SHL scraper (build catalog from train set)."""

import sys

from app.core.config import settings

# Add SHL module to path (shl_recommendation_system contains scraper/)
_shl_path = settings.shl_module_path
if str(_shl_path) not in sys.path:
    sys.path.insert(0, str(_shl_path))


class ScraperService:
    """Business logic for SHL catalog building. Uses existing scraper."""

    def build_catalog_from_train(self) -> list[dict]:
        """Build catalog from train set when live scraping is blocked."""
        try:
            from scraper.build_from_train import build_catalog_from_train  # noqa: PLC0415

            return build_catalog_from_train()
        except ImportError as e:
            from app.core.exceptions import RecommendationError

            raise RecommendationError(
                message="Scraper module not available",
                details={"import_error": str(e)},
            ) from e
        except Exception as e:
            from app.core.exceptions import RecommendationError

            raise RecommendationError(
                message=str(e),
                details=None,
            ) from e
