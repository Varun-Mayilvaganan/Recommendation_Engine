"""Custom business and application exceptions."""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class RecommendationError(AppException):
    """Error in recommendation pipeline."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(
            message=message,
            error_code="RECOMMENDATION_ERROR",
            details=details,
        )
