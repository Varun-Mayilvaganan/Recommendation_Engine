"""Controllers - API route handlers."""

from app.controllers.recommendation_controller import router as recommendation_router
from app.controllers.user_controller import router as user_router

__all__ = ["user_router", "recommendation_router"]
