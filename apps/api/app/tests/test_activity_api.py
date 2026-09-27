from datetime import datetime, timezone
from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
    ActivityEvent,
)
from app.tests.conftest import TestSessionLocal


def test_activity_timeline_api(client, test_user):
    """
    Verify that the activity timeline API returns
    recent activity for a user.
    """

    db = TestSessionLocal()

    try:
        db.add(
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_created,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                event_metadata={
                    "title": "API test task",
                },
            )
        )

        db.commit()

    finally:
        db.close()

    response = client.get(
        "/api/v1/activity/timeline",
        params={
            "user_id": str(test_user.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == str(test_user.id)
    assert data[0]["event_type"] == "task_created"
    assert data[0]["entity_type"] == "task"


def test_activity_range_api(client, test_user):
    """
    Verify that the activity range API returns
    events within the requested time range.
    """

    db = TestSessionLocal()

    try:
        event_time = datetime(
            2026,
            9,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )

        db.add(
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_completed,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            )
        )

        db.commit()

    finally:
        db.close()

    response = client.get(
        "/api/v1/activity/range",
        params={
            "user_id": str(test_user.id),
            "start": "2026-09-26T00:00:00+00:00",
            "end": "2026-09-26T23:59:59+00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["event_type"] == "task_completed"


def test_activity_entity_api(client, test_user):
    """
    Verify that the entity history API returns
    activity for a specific entity.
    """

    entity_id = uuid4()

    db = TestSessionLocal()

    try:
        db.add_all(
            [
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.task_created,
                    entity_type=ActivityEntityType.task,
                    entity_id=entity_id,
                ),
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.task_completed,
                    entity_type=ActivityEntityType.task,
                    entity_id=entity_id,
                ),
            ]
        )

        db.commit()

    finally:
        db.close()

    response = client.get(
        f"/api/v1/activity/entity/task/{entity_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    for event in data:
        assert event["entity_id"] == str(entity_id)
        assert event["entity_type"] == "task"


def test_activity_summary_api(client, test_user):
    """
    Verify that the activity summary API returns
    event counts for a time range.
    """

    event_time = datetime(
        2026,
        9,
        26,
        12,
        0,
        tzinfo=timezone.utc,
    )

    db = TestSessionLocal()

    try:
        db.add_all(
            [
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.task_created,
                    entity_type=ActivityEntityType.task,
                    entity_id=uuid4(),
                    occurred_at=event_time,
                ),
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.task_completed,
                    entity_type=ActivityEntityType.task,
                    entity_id=uuid4(),
                    occurred_at=event_time,
                ),
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.task_completed,
                    entity_type=ActivityEntityType.task,
                    entity_id=uuid4(),
                    occurred_at=event_time,
                ),
                ActivityEvent(
                    user_id=test_user.id,
                    event_type=ActivityEventType.habit_completed,
                    entity_type=ActivityEntityType.habit,
                    entity_id=uuid4(),
                    occurred_at=event_time,
                ),
            ]
        )

        db.commit()

    finally:
        db.close()

    response = client.get(
        "/api/v1/activity/summary",
        params={
            "user_id": str(test_user.id),
            "start": "2026-09-26T00:00:00+00:00",
            "end": "2026-09-26T23:59:59+00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 4
    assert data["by_event_type"]["task_created"] == 1
    assert data["by_event_type"]["task_completed"] == 2
    assert data["by_event_type"]["habit_completed"] == 1
