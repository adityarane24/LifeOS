# ---------------------------------------------------------
# ANALYTICS API ROUTES
# ---------------------------------------------------------
#
# These endpoints expose LifeOS personal activity analytics.
#
# Route
#   ↓
# ActivityAnalyticsService
#   ↓
# TemporalActivityService
#   ↓
# ActivityEventRepository
#   ↓
# PostgreSQL
#
# These endpoints are read-only.
# Analytics are calculated from immutable activity events.
# ---------------------------------------------------------

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.activity_analytics import ActivityAnalyticsService


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ---------------------------------------------------------
# USER ANALYTICS
# ---------------------------------------------------------

@router.get(
    "",
)
def get_user_analytics(
    user_id: UUID,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db),
):
    """
    Return personal activity analytics for a time range.
    """

    service = ActivityAnalyticsService(db)

    return service.get_user_analytics(
        user_id=user_id,
        start=start,
        end=end,
    )
