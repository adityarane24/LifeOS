# ---------------------------------------------------------
# USER SERVICE
# ---------------------------------------------------------
#
# The service layer contains business logic.
#
# Architecture:
#
# API Route
#     ↓
# Service
#     ↓
# Repository
#     ↓
# Database


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """
    Contains business logic related to users.
    """

    def __init__(self, db: Session):
        """
        Create the service using the current database
        session.
        """

        self.db = db

        # Create the repository that will handle
        # database operations.
        self.repository = UserRepository(db)

    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    def create_user(self, data: UserCreate) -> User:
        """
        Create a new LifeOS user.

        Business rules:
        1. Email must not already exist.
        2. Create the User model.
        3. Save it through the repository.
        4. Commit the transaction.
        """

        # Check whether the email is already registered.
        existing_user = self.repository.get_by_email(
            str(data.email)
        )

        if existing_user:
            # Raise an error that our API layer will
            # eventually convert into an HTTP 409 response.
            raise ValueError(
                "A user with this email already exists."
            )

        # Create the SQLAlchemy model.
        user = User(
            email=str(data.email),
            name=data.name,
        )

        try:
            # Add the user to the current transaction.
            self.repository.create(user)

            # Permanently save the transaction.
            self.db.commit()

            # Refresh the object so database-generated
            # values such as timestamps are available.
            self.db.refresh(user)

            return user

        except IntegrityError:
            # Something violated a database constraint.
            #
            # Roll back the transaction so the session
            # remains usable.
            self.db.rollback()

            raise