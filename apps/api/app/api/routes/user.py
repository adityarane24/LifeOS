# ---------------------------------------------------------
# USER API ROUTES
# ---------------------------------------------------------
#
# This file contains HTTP endpoints related to users.
#
# The route should remain thin.
#
# Route
#   ↓
# Schema validation
#   ↓
# Service
#   ↓
# Repository
#   ↓
# Database


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService


# Create a router specifically for user endpoints.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------------------------------------------------------
# CREATE USER
# ---------------------------------------------------------


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new LifeOS user.
    """

    # Create the service using the current DB session.
    service = UserService(db)

    try:
        # Ask the service to perform the business logic.
        user = service.create_user(data)

        # Return the newly created user.
        return user

    except ValueError as error:
        # Convert our business error into an HTTP 409.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )