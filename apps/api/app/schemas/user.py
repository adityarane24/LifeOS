# ---------------------------------------------------------
# USER API SCHEMAS
# ---------------------------------------------------------
#
# Schemas define the data that enters and leaves our API.
#
# IMPORTANT:
#
# SQLAlchemy Model
#     ↓
# Represents database structure
#
# Pydantic Schema
#     ↓
# Represents API data


from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------
# CREATE USER REQUEST
# ---------------------------------------------------------


class UserCreate(BaseModel):
    """
    Data required to create a new LifeOS user.
    """

    # Email address supplied by the client.
    #
    # EmailStr makes Pydantic validate that the value
    # has a valid email format.
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