# ---------------------------------------------------------
# Recommendation API Routes
# ---------------------------------------------------------
#
# Route → Service → Repository → PostgreSQL
# ---------------------------------------------------------

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationStatusUpdate,
)
from app.services.recommendation import RecommendationService


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


# ---------------------------------------------------------
# GET USER RECOMMENDATIONS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[RecommendationResponse],
)
def get_user_recommendations(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return all recommendations belonging to a user.
    """

    service = RecommendationService(db)

    return service.get_user_recommendations(user_id)


# ---------------------------------------------------------
# GET SINGLE RECOMMENDATION
# ---------------------------------------------------------

@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return a single recommendation.
    """

    service = RecommendationService(db)

    recommendation = service.get_recommendation(
        recommendation_id
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation


# ---------------------------------------------------------
# UPDATE RECOMMENDATION STATUS
# ---------------------------------------------------------

@router.patch(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def update_recommendation_status(
    recommendation_id: UUID,
    data: RecommendationStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the lifecycle status of a recommendation.
    """

    service = RecommendationService(db)

    recommendation = service.update_status(
        recommendation_id,
        data.status,
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation