# ---------------------------------------------------------
# Recommendation API Schemas
# ---------------------------------------------------------
#
# These schemas define the data sent to and returned from
# the Recommendation API.
# ---------------------------------------------------------

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# RECOMMENDATION RESPONSE
# ---------------------------------------------------------

class RecommendationResponse(BaseModel):
    """
    Data returned to the client for a recommendation.
    """

    id: UUID

    user_id: UUID

    recommendation_type: str

    title: str

    message: str

    reason: str | None

    source_signal: str | None

    priority: float

    status: str

    generated_at: datetime

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------------------------------------------------------
# RECOMMENDATION STATUS UPDATE
# ---------------------------------------------------------

class RecommendationStatusUpdate(BaseModel):
    """
    Data used to update the lifecycle status of a
    recommendation.
    """

    status: str = Field(
        min_length=1,
        max_length=50,
    )