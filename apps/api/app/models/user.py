# ---------------------------------------------------------
# User Database Model
# ---------------------------------------------------------
#
# This file defines the User table used by LifeOS.
#
# SQLAlchemy will use this Python class to describe the
# structure of the "users" table in PostgreSQL.


from datetime import datetime

# UUID is Python's built-in UUID type.
from uuid import UUID, uuid4

# SQLAlchemy column types and configuration.
from sqlalchemy import Boolean, DateTime, String, func, true

# SQLAlchemy ORM tools.
from sqlalchemy.orm import Mapped, mapped_column

# Our common SQLAlchemy Base.
from app.db.base import Base

from pydantic import BaseModel, EmailStr, Field

class User(Base):
    """
    Represents a user in LifeOS.

    Each User object corresponds to one row in the
    PostgreSQL "users" table.
    """

    # -----------------------------------------------------
    # TABLE NAME
    # -----------------------------------------------------
    #
    # By default SQLAlchemy can generate table names, but
    # explicitly defining the name makes our database
    # structure easier to understand.
    __tablename__ = "users"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------
    #
    # Every user needs a unique identifier.
    #
    # UUIDs are globally unique identifiers.
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------
    #
    # Email will eventually be used as the user's login
    # identifier.
    #
    # unique=True prevents two users from having the same
    # email address.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # NAME
    # -----------------------------------------------------
    #
    # The user's display name.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # -----------------------------------------------------
    # ACTIVE STATUS
    # -----------------------------------------------------
    #
    # True  -> account is active
    # False -> account has been deactivated
    is_active: Mapped[bool] = mapped_column(
        Boolean,

        # Python-side default.
        default=True,

        # Database-side default.
        #
        # This means PostgreSQL will also use TRUE when
        # a value isn't explicitly supplied.
        server_default=true(),

        nullable=False,
)

    # -----------------------------------------------------
    # CREATED AT
    # -----------------------------------------------------
    #
    # PostgreSQL generates the timestamp when the row
    # is created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # -----------------------------------------------------
    # UPDATED AT
    # -----------------------------------------------------
    #
    # This records when the row was last modified.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


    # ---------------------------------------------------------

# CREATE USER REQUEST

# ---------------------------------------------------------

class UserCreate(BaseModel):

    """
    Data required to create a new LifeOS user.
    """

    # Email address supplied by the client.
    #
    # EmailStr makes Pydantic validate that the value has a valid email format.

    email: EmailStr

    # Display name supplied by the client.
    #
    # Field allows us to define validation rules.

    name: str = Field(
        min_length=1,
        max_length=100,
    )

# ---------------------------------------------------------
# USER RESPONSE
# ---------------------------------------------------------

class UserResponse(BaseModel):
    """
    Data returned to the client after a user is created.
    """

    # User's unique identifier.
    id: UUID

    # User's email address.
    email: EmailStr

    # User's display name.
    name: str

    # Whether the account is active.
    is_active: bool

    # Tell Pydantic that this schema can be created

    # from an ORM/SQLAlchemy object.

    model_config = {

        "from_attributes": True

    }