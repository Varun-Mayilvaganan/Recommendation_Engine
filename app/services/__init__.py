"""Services - business logic. No direct DB access."""

from app.services.recommendation_service import RecommendationService
from app.services.scraper_service import ScraperService
from app.services.user_service import UserService

__all__ = ["UserService", "RecommendationService", "ScraperService"]
