from datetime import datetime, timedelta, timezone

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.tests.conftest import TestSessionLocal


def test_get_user_analytics(client, test_user):
    db = TestSessionLocal()

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    end = now + timedelta(days=1)

    events = [
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.goal_completed,
            entity_type=ActivityEntityType.goal,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.habit_completed,
            entity_type=ActivityEntityType.habit,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.habit_missed,
            entity_type=ActivityEntityType.habit,
            entity_id=test_user.id,
            occurred_at=now,
        ),
        ActivityEvent(
            user_id=test_user.id,
            event_type=ActivityEventType.project_completed,
            entity_type=ActivityEntityType.project,
            entity_id=test_user.id,
            occurred_at=now,
        ),
    ]

    db.add_all(events)
    db.commit()
    db.close()

    response = client.get(
        "/api/v1/analytics",
        params={
            "user_id": str(test_user.id),
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 7

    assert data["tasks"]["created"] == 2
    assert data["tasks"]["completed"] == 1
    assert data["tasks"]["completion_rate"] == 50.0

    assert data["goals"]["completed"] == 1

    assert data["habits"]["completed"] == 1
    assert data["habits"]["missed"] == 1
    assert data["habits"]["consistency_rate"] == 50.0

    assert data["projects"]["completed"] == 1


def test_get_user_analytics_empty_range(client, test_user):
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 1, 2, tzinfo=timezone.utc)

    response = client.get(
        "/api/v1/analytics",
        params={
            "user_id": str(test_user.id),
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 0

    assert data["tasks"]["created"] == 0
    assert data["tasks"]["completed"] == 0
    assert data["tasks"]["completion_rate"] == 0

    assert data["goals"]["completed"] == 0

    assert data["habits"]["completed"] == 0
    assert data["habits"]["missed"] == 0
    assert data["habits"]["consistency_rate"] == 0

    assert data["projects"]["completed"] == 0
