"""Standard API response builder.

Every API must return:
{
    "data": <actual_data_or_null>,
    "message": "success or failure message",
    "error": <error_message_or_null>,
    "error_code": <error_code_or_null>
}
"""

from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    """Build standardized success response."""
    payload = {
        "data": data,
        "message": message,
        "error": None,
        "error_code": None,
    }
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    message: str = "An error occurred",
    error: str | None = None,
    error_code: str | None = None,
    status_code: int = 500,
) -> JSONResponse:
    """Build standardized error response."""
    payload = {
        "data": None,
        "message": message,
        "error": error or message,
        "error_code": error_code,
    }
    return JSONResponse(status_code=status_code, content=payload)
