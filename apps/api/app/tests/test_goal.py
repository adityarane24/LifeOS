# ---------------------------------------------------------
# Goal API Tests
# ---------------------------------------------------------
#
# These tests verify the Goal API from the HTTP layer
# all the way to the PostgreSQL test database.

from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.tests.conftest import TestSessionLocal


def create_test_user(client):
    """
    Create a user that can own our test goals.

    Goals require a valid user_id because of the
    foreign-key relationship with the users table.
    """
    response = client.post(
        "/api/v1/users",
        json={
            "email": f"{uuid4()}@example.com",
            "name": "Goal Test User",
        },
    )

    assert response.status_code == 201

    user_data = response.json()

    return user_data["id"]


def test_create_goal(client):
    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "learn python",
            "description": "complete python course",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user_id
    assert data["title"] == "learn python"
    assert data["description"] == "complete python course"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["progress"] == 0
    assert data["target_date"] is None


def test_create_goal_with_progress(client):
    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "learn machine learning",
            "progress": 25,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["progress"] == 25


def test_create_goal_with_empty_title(client):
    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "",
        },
    )

    assert response.status_code == 422


def test_create_goal_with_invalid_progress(client):
    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "learn python",
            "progress": 101,
        },
    )

    assert response.status_code == 422


def test_get_user_goals(client):
    user_id = create_test_user(client)

    client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "goal one",
        },
    )

    client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "goal two",
        },
    )

    response = client.get(
        f"/api/v1/goals?user_id={user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "goal two"
    assert data[1]["title"] == "goal one"


def test_get_goal(client):
    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "become a data scientist",
        },
    )

    goal_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/goals/{goal_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == goal_id
    assert data["title"] == "become a data scientist"


def test_get_nonexistent_goal(client):
    goal_id = uuid4()

    response = client.get(
        f"/api/v1/goals/{goal_id}"
    )

    assert response.status_code == 404


def test_update_goal(client):
    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "study python",
            "priority": "medium",
        },
    )

    goal_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={
            "priority": "urgent",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "study python"
    assert data["priority"] == "urgent"


def test_update_multiple_goal_fields(client):
    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "old goal",
            "priority": "low",
        },
    )

    goal_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={
            "title": "new goal",
            "status": "in_progress",
            "priority": "high",
            "progress": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "new goal"
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"
    assert data["progress"] == 50


def test_update_goal_with_invalid_progress(client):
    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "learn python",
        },
    )

    goal_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={
            "progress": 101,
        },
    )

    assert response.status_code == 422


def test_update_nonexistent_goal(client):
    goal_id = uuid4()

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={
            "progress": 50,
        },
    )

    assert response.status_code == 404


def test_delete_goal(client):
    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/goals",
        json={
            "user_id": user_id,
            "title": "temporary goal",
        },
    )

    goal_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/goals/{goal_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/goals/{goal_id}"
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_goal(client):
    goal_id = uuid4()

    response = client.delete(
        f"/api/v1/goals/{goal_id}"
    )

    assert response.status_code == 404



def test_create_goal_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that creating a goal creates
    a goal_created activity event.
    """

    response = client.post(
        "/api/v1/goals/",
        json={
            "user_id": str(test_user.id),
            "title": "Learn Python",
            "description": "Complete Python learning path",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    goal = response.json()

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == goal["id"],
                ActivityEvent.event_type
                == ActivityEventType.goal_created,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.goal

    finally:
        db.close()


def test_update_goal_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that updating a goal creates
    a goal_updated activity event.
    """

    create_response = client.post(
        "/api/v1/goals/",
        json={
            "user_id": str(test_user.id),
            "title": "Original Goal",
            "description": "Original description",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    goal = create_response.json()

    update_response = client.patch(
        f"/api/v1/goals/{goal['id']}",
        json={
            "title": "Updated Goal",
        },
    )

    assert update_response.status_code == 200

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == goal["id"],
                ActivityEvent.event_type
                == ActivityEventType.goal_updated,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.goal
        assert event.event_metadata["updated_fields"] == [
            "title"
        ]

    finally:
        db.close()


def test_update_goal_progress_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that changing goal progress creates
    a goal_progress_updated activity event.
    """

    create_response = client.post(
        "/api/v1/goals/",
        json={
            "user_id": str(test_user.id),
            "title": "Progress Goal",
            "description": "Track progress",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    goal = create_response.json()

    update_response = client.patch(
        f"/api/v1/goals/{goal['id']}",
        json={
            "progress": 50,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["progress"] == 50

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == goal["id"],
                ActivityEvent.event_type
                == ActivityEventType.goal_progress_updated,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.goal
        assert event.event_metadata["old_progress"] == 0
        assert event.event_metadata["new_progress"] == 50

    finally:
        db.close()


def test_complete_goal_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that completing a goal creates
    a goal_completed activity event.
    """

    create_response = client.post(
        "/api/v1/goals/",
        json={
            "user_id": str(test_user.id),
            "title": "Complete Goal",
            "description": "Goal for completion test",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    goal = create_response.json()

    update_response = client.patch(
        f"/api/v1/goals/{goal['id']}",
        json={
            "status": "completed",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == goal["id"],
                ActivityEvent.event_type
                == ActivityEventType.goal_completed,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.goal
        assert event.event_metadata["old_status"] == "pending"
        assert event.event_metadata["new_status"] == "completed"

    finally:
        db.close()


def test_cancel_goal_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that cancelling a goal creates
    a goal_cancelled activity event.
    """

    create_response = client.post(
        "/api/v1/goals/",
        json={
            "user_id": str(test_user.id),
            "title": "Cancel Goal",
            "description": "Goal for cancellation test",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    goal = create_response.json()

    update_response = client.patch(
        f"/api/v1/goals/{goal['id']}",
        json={
            "status": "cancelled",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "cancelled"

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == goal["id"],
                ActivityEvent.event_type
                == ActivityEventType.goal_cancelled,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.goal
        assert event.event_metadata["old_status"] == "pending"
        assert event.event_metadata["new_status"] == "cancelled"

    finally:
        db.close()