from datetime import date, timedelta

from app.models.habit import HabitFrequency

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.tests.conftest import TestSessionLocal


def test_create_habit(client, test_user):
    response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Study Python"
    assert data["frequency"] == "daily"
    assert data["target"] == 1
    assert data["unit"] == "times"
    assert data["is_active"] is True


def test_create_habit_with_custom_values(client, test_user):
    response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
            "description": "Practice Python for one hour",
            "frequency": "weekly",
            "days_of_week": [
                "monday",
                "wednesday",
                "friday",
            ],
            "target": 60,
            "unit": "minutes",
            "start_date": "2026-09-15",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["frequency"] == "weekly"
    assert data["days_of_week"] == [
        "monday",
        "wednesday",
        "friday",
    ]
    assert data["target"] == 60
    assert data["unit"] == "minutes"


def test_create_habit_with_empty_title(client, test_user):
    response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "",
        },
    )

    assert response.status_code == 422


def test_create_habit_with_invalid_target(client, test_user):
    response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
            "target": 0,
        },
    )

    assert response.status_code == 422


def test_get_habit(client, test_user):
    create_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Go to Gym",
        },
    )

    habit_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/habits/{habit_id}"
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Go to Gym"


def test_get_user_habits(client, test_user):
    client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study",
        },
    )

    client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Exercise",
        },
    )

    response = client.get(
        f"/api/v1/habits?user_id={test_user.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_nonexistent_habit(client):
    response = client.get(
        "/api/v1/habits/00000000-0000-0000-0000-000000000001"
    )

    assert response.status_code == 404


def test_update_habit(client, test_user):
    create_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
        },
    )

    habit_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/habits/{habit_id}",
        json={
            "title": "Study Advanced Python",
            "target": 60,
            "unit": "minutes",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Study Advanced Python"
    assert data["target"] == 60
    assert data["unit"] == "minutes"


def test_delete_habit(client, test_user):
    create_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Temporary Habit",
        },
    )

    habit_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/habits/{habit_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/habits/{habit_id}"
    )

    assert get_response.status_code == 404


def test_create_completion(client, test_user):
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
        },
    )

    habit_id = habit_response.json()["id"]

    response = client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json={
            "completion_date": "2026-09-15",
            "value": 60,
            "completed": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["habit_id"] == habit_id
    assert data["completion_date"] == "2026-09-15"
    assert data["value"] == 60
    assert data["completed"] is True


def test_duplicate_completion_is_rejected(
    client,
    test_user,
):
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Read",
        },
    )

    habit_id = habit_response.json()["id"]

    completion_data = {
        "completion_date": "2026-09-15",
        "value": 20,
        "completed": True,
    }

    first_response = client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json=completion_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json=completion_data,
    )

    assert second_response.status_code == 400
    assert "already recorded" in second_response.json()["detail"]


def test_inactive_habit_cannot_be_completed(
    client,
    test_user,
):
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Paused Habit",
            "is_active": False,
        },
    )

    habit_id = habit_response.json()["id"]

    response = client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json={
            "completion_date": "2026-09-15",
            "value": 1,
            "completed": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Habit is inactive"


def test_get_completions(client, test_user):
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Read",
        },
    )

    habit_id = habit_response.json()["id"]

    client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json={
            "completion_date": "2026-09-14",
            "value": 10,
            "completed": True,
        },
    )

    client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json={
            "completion_date": "2026-09-15",
            "value": 20,
            "completed": True,
        },
    )

    response = client.get(
        f"/api/v1/habits/{habit_id}/completions"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_delete_completion(client, test_user):
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Read",
        },
    )

    habit_id = habit_response.json()["id"]

    client.post(
        f"/api/v1/habits/{habit_id}/completions",
        json={
            "completion_date": "2026-09-15",
            "value": 20,
            "completed": True,
        },
    )

    response = client.delete(
        f"/api/v1/habits/{habit_id}/completions/2026-09-15"
    )

    assert response.status_code == 204

    completions_response = client.get(
        f"/api/v1/habits/{habit_id}/completions"
    )

    assert completions_response.status_code == 200
    assert completions_response.json() == []


def test_get_habit_analytics(client, test_user):
    """
    Test the habit analytics API endpoint.
    """

    today = date.today()

    # Start the habit six days before today.
    start_date = today - timedelta(days=5)

    # Create a habit.
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
            "start_date": start_date.isoformat(),
        },
    )

    assert habit_response.status_code == 201

    habit_id = habit_response.json()["id"]

    # Add three completed days.
    #
    # The first three days are missed.
    # The final three days are completed.
    #
    # Example:
    #
    # Day -5  ❌
    # Day -4  ❌
    # Day -3  ❌
    # Day -2  ✅
    # Day -1  ✅
    # Today   ✅
    #
    # Therefore:
    # current_streak = 3
    # longest_streak = 3
    # completion_rate = 50%
    for completion_date in [
        today - timedelta(days=2),
        today - timedelta(days=1),
        today,
    ]:
        response = client.post(
            f"/api/v1/habits/{habit_id}/completions",
            json={
                "completion_date": completion_date.isoformat(),
                "value": 60,
                "completed": True,
            },
        )

        assert response.status_code == 201

    # Request analytics.
    response = client.get(
        f"/api/v1/habits/{habit_id}/analytics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["habit_id"] == habit_id
    assert data["current_streak"] == 3
    assert data["longest_streak"] == 3
    assert data["completion_rate"] == 50.0



def test_create_habit_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that creating a habit creates
    a habit_created activity event.
    """

    response = client.post(
        "/api/v1/habits/",
        json={
            "user_id": str(test_user.id),
            "title": "Morning Exercise",
            "description": "Exercise every morning",
            "frequency": "daily",
            "target": 1,
            "unit": "times",
        },
    )

    assert response.status_code == 201

    habit = response.json()

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == habit["id"],
                ActivityEvent.event_type
                == ActivityEventType.habit_created,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.habit

    finally:
        db.close()


def test_update_habit_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that updating a habit creates
    a habit_updated activity event.
    """

    create_response = client.post(
        "/api/v1/habits/",
        json={
            "user_id": str(test_user.id),
            "title": "Read Book",
            "description": "Read every day",
            "frequency": "daily",
            "target": 1,
            "unit": "times",
        },
    )

    assert create_response.status_code == 201

    habit = create_response.json()

    update_response = client.patch(
        f"/api/v1/habits/{habit['id']}",
        json={
            "title": "Read Technical Book",
        },
    )

    assert update_response.status_code == 200

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == habit["id"],
                ActivityEvent.event_type
                == ActivityEventType.habit_updated,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.habit
        assert event.event_metadata["updated_fields"] == [
            "title"
        ]

    finally:
        db.close()


def test_complete_habit_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that completing a habit creates
    a habit_completed activity event.
    """

    create_response = client.post(
        "/api/v1/habits/",
        json={
            "user_id": str(test_user.id),
            "title": "Drink Water",
            "description": "Drink enough water",
            "frequency": "daily",
            "target": 1,
            "unit": "times",
        },
    )

    assert create_response.status_code == 201

    habit = create_response.json()

    completion_response = client.post(
        f"/api/v1/habits/{habit['id']}/completions",
        json={
            "completion_date": "2026-09-27",
            "value": 1,
            "completed": True,
        },
    )

    assert completion_response.status_code == 201

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == habit["id"],
                ActivityEvent.event_type
                == ActivityEventType.habit_completed,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.habit
        assert event.event_metadata["completion_date"] == (
            "2026-09-27"
        )
        assert event.event_metadata["value"] == 1
        assert event.event_metadata["completed"] is True

    finally:
        db.close()


def test_missed_habit_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that recording an incomplete habit creates
    a habit_missed activity event.
    """

    create_response = client.post(
        "/api/v1/habits/",
        json={
            "user_id": str(test_user.id),
            "title": "Meditation",
            "description": "Meditate every morning",
            "frequency": "daily",
            "target": 1,
            "unit": "times",
        },
    )

    assert create_response.status_code == 201

    habit = create_response.json()

    completion_response = client.post(
        f"/api/v1/habits/{habit['id']}/completions",
        json={
            "completion_date": "2026-09-27",
            "value": 0,
            "completed": False,
        },
    )

    assert completion_response.status_code == 201

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == habit["id"],
                ActivityEvent.event_type
                == ActivityEventType.habit_missed,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.habit
        assert event.event_metadata["completion_date"] == (
            "2026-09-27"
        )
        assert event.event_metadata["completed"] is False

    finally:
        db.close()


def test_deactivate_habit_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that deactivating a habit creates
    a habit_deactivated activity event.
    """

    create_response = client.post(
        "/api/v1/habits/",
        json={
            "user_id": str(test_user.id),
            "title": "Old Habit",
            "description": "Habit to deactivate",
            "frequency": "daily",
            "target": 1,
            "unit": "times",
        },
    )

    assert create_response.status_code == 201

    habit = create_response.json()

    update_response = client.patch(
        f"/api/v1/habits/{habit['id']}",
        json={
            "is_active": False,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == habit["id"],
                ActivityEvent.event_type
                == ActivityEventType.habit_deactivated,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.habit
        assert event.event_metadata["old_is_active"] is True
        assert event.event_metadata["new_is_active"] is False

    finally:
        db.close()