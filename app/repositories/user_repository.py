"""User repository - database CRUD operations only. No business logic."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.models.user import User


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, email: str, name: str | None = None) -> User:
        """Create a new user. Raises ValidationError on duplicate email."""
        try:
            user = User(email=email, name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise ValidationError(
                    message="User with this email already exists",
                    details={"email": email},
                ) from e
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, email: str | None = None, name: str | None = None) -> User | None:
        """Update user. Returns updated user or None if not found."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        try:
            if email is not None:
                user.email = email
            if name is not None:
                user.name = name
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower():
                raise ValidationError(
                    message="User with this email already exists",
                    details={"email": email},
                ) from e
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete(self, user_id: int) -> bool:
        """Delete user. Returns True if deleted, False if not found."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
