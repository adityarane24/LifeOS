# ---------------------------------------------------------
# ACTIVITY API ROUTES
# ---------------------------------------------------------
#
# These endpoints expose LifeOS activity history.
#
# Route
#   ↓
# TemporalActivityService
#   ↓
# ActivityEventService
#   ↓
# ActivityEventRepository
#   ↓
# PostgreSQL
#
# Activity events are created by the domain services
# (TaskService, GoalService, HabitService, ProjectService).
#
# These routes are read-only.
# ---------------------------------------------------------

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.activity_event import ActivityEntityType
from app.schemas.activity_event import ActivityEventResponse
from app.services.temporal_activity import TemporalActivityService


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/activity",
    tags=["Activity"],
)


# ---------------------------------------------------------
# RECENT TIMELINE
# ---------------------------------------------------------

@router.get(
    "/timeline",
    response_model=list[ActivityEventResponse],
)
def get_activity_timeline(
    user_id: UUID,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    """
    Return the most recent activity for a user.
    """

    service = TemporalActivityService(db)

    return service.get_timeline(
        user_id=user_id,
        limit=limit,
    )


# ---------------------------------------------------------
# ACTIVITY BETWEEN TWO TIMES
# ---------------------------------------------------------

@router.get(
    "/range",
    response_model=list[ActivityEventResponse],
)
def get_activity_range(
    user_id: UUID,
    start: datetime,
    end: datetime,
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    db: Session = Depends(get_db),
):
    """
    Return activity that occurred between two timestamps.
    """

    service = TemporalActivityService(db)

    return service.get_activity_between(
        user_id=user_id,
        start=start,
        end=end,
        limit=limit,
    )


# ---------------------------------------------------------
# ENTITY HISTORY
# ---------------------------------------------------------

@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=list[ActivityEventResponse],
)
def get_entity_activity(
    entity_type: ActivityEntityType,
    entity_id: UUID,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):
    """
    Return activity history for one entity.

    Example:
        /api/v1/activity/entity/task/<task_id>
    """

    service = TemporalActivityService(db)

    return service.get_entity_history(
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )


# ---------------------------------------------------------
# ACTIVITY SUMMARY
# ---------------------------------------------------------

@router.get(
    "/summary",
)
def get_activity_summary(
    user_id: UUID,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db),
):
    """
    Return an activity summary for a time range.
    """

    service = TemporalActivityService(db)

    return service.get_activity_summary(
        user_id=user_id,
        start=start,
        end=end,
    )
