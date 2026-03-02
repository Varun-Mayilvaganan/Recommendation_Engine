"""User controller - API route handlers. Request validation, service calls, exception handling."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppException, NotFoundError, ValidationError
from app.core.logger import log_api_entry, log_api_error, log_api_success
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new user."""
    endpoint = "POST /users"
    log_api_entry(endpoint, "POST", email=payload.email)

    try:
        service = UserService(db)
        user = service.create_user(payload)
        log_api_success(endpoint, f"User created: id={user.id}")
        return success_response(
            data=UserResponse.model_validate(user).model_dump(mode="json"),
            message="User created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except ValidationError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except AppException as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to create user",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Get user by ID."""
    endpoint = f"GET /users/{user_id}"
    log_api_entry(endpoint, "GET", user_id=user_id)

    try:
        service = UserService(db)
        user = service.get_user_by_id(user_id)
        log_api_success(endpoint, f"User found: id={user_id}")
        return success_response(
            data=UserResponse.model_validate(user).model_dump(mode="json"),
            message="User retrieved successfully",
        )
    except NotFoundError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to retrieve user",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    """List all users with pagination."""
    endpoint = "GET /users"
    log_api_entry(endpoint, "GET", skip=skip, limit=limit)

    try:
        service = UserService(db)
        users = service.get_all_users(skip=skip, limit=limit)
        data = [UserResponse.model_validate(u).model_dump(mode="json") for u in users]
        log_api_success(endpoint, f"Returned {len(data)} users")
        return success_response(
            data=data,
            message="Users retrieved successfully",
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to list users",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update user by ID."""
    endpoint = f"PATCH /users/{user_id}"
    log_api_entry(endpoint, "PATCH", user_id=user_id)

    try:
        service = UserService(db)
        user = service.update_user(user_id, payload)
        log_api_success(endpoint, f"User updated: id={user_id}")
        return success_response(
            data=UserResponse.model_validate(user).model_dump(mode="json"),
            message="User updated successfully",
        )
    except NotFoundError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except ValidationError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to update user",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete user by ID."""
    endpoint = f"DELETE /users/{user_id}"
    log_api_entry(endpoint, "DELETE", user_id=user_id)

    try:
        service = UserService(db)
        service.delete_user(user_id)
        log_api_success(endpoint, f"User deleted: id={user_id}")
        return success_response(
            data=None,
            message="User deleted successfully",
        )
    except NotFoundError as e:
        log_api_error(endpoint, str(e), e.error_code)
        return error_response(
            message=e.message,
            error=str(e),
            error_code=e.error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        log_api_error(endpoint, str(e))
        return error_response(
            message="Failed to delete user",
            error=str(e),
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
