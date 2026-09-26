# ---------------------------------------------------------
# USER REPOSITORY
# ---------------------------------------------------------
#
# The repository is responsible for database operations
# related to users.
#
# It should NOT contain business decisions.
#
# Its job is:
#
# Service
#    ↓
# Repository
#    ↓
# SQLAlchemy
#    ↓
# PostgreSQL


from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Handles database operations for User objects.
    """

    def __init__(self, db: Session):
        """
        Store the database session used by this repository.
        """

        self.db = db

    # -----------------------------------------------------
    # FIND USER BY EMAIL
    # -----------------------------------------------------

    def get_by_email(self, email: str) -> User | None:
        """
        Find a user using their email address.

        Returns:
            User object if found.
            None if no user exists.
        """

        # Build a SELECT query.
        statement = select(User).where(
            User.email == email
        )

        # Execute the query.
        result = self.db.execute(statement)

        # Return the first matching user, if one exists.
        return result.scalar_one_or_none()

    # -----------------------------------------------------
    # FIND USER BY ID
    # -----------------------------------------------------

    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Find a user using their UUID.
        """

        # Build a SELECT query.
        statement = select(User).where(
            User.id == user_id
        )

        # Execute the query.
        result = self.db.execute(statement)

        # Return the user if found.
        return result.scalar_one_or_none()

    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    def create(self, user: User) -> User:
        """
        Add a User object to the current database session.

        The service layer will decide when to commit.
        """

        # Add the object to SQLAlchemy's session.
        self.db.add(user)

        # Flush pending changes to PostgreSQL.
        #
        # flush() sends the INSERT to the database without
        # permanently committing the transaction yet.
        self.db.flush()

        # Return the SQLAlchemy User object.
        return user