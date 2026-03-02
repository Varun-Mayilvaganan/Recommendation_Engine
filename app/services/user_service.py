"""User service - business logic. No database access directly. Calls repository."""

from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session


class UserService:
    """Business logic for user operations."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def create_user(self, payload: UserCreate):
        """Create a new user. Raises ValidationError if email exists."""
        existing = self.repository.get_by_email(payload.email)
        if existing:
            raise ValidationError(
                message="User with this email already exists",
                details={"email": payload.email},
            )
        return self.repository.create(
            email=payload.email,
            name=payload.name,
        )

    def get_user_by_id(self, user_id: int):
        """Get user by ID. Raises NotFoundError if not found."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(resource="User", identifier=user_id)
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100):
        """Get paginated list of users."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, payload: UserUpdate):
        """Update user. Raises NotFoundError if not found."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(resource="User", identifier=user_id)
        return self.repository.update(
            user_id=user_id,
            email=payload.email,
            name=payload.name,
        )

    def delete_user(self, user_id: int) -> None:
        """Delete user. Raises NotFoundError if not found."""
        deleted = self.repository.delete(user_id)
        if not deleted:
            raise NotFoundError(resource="User", identifier=user_id)
