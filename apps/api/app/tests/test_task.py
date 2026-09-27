# ---------------------------------------------------------
# Task API Tests
# ---------------------------------------------------------
#
# These tests verify the Task API from the HTTP layer
# all the way to the PostgreSQL test database.


from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.tests.conftest import TestSessionLocal


# ---------------------------------------------------------
# HELPER — CREATE TEST USER
# ---------------------------------------------------------

def create_test_user(client):
    """
    Create a user that can own our test tasks.

    Tasks require a valid user_id because of the
    foreign-key relationship with the users table.
    """

    response = client.post(
        "/api/v1/users",
        json={
            "email": f"{uuid4()}@example.com",
            "name": "Task Test User",
        },
    )

    assert response.status_code == 201

    user_data = response.json()

    return user_data["id"]


# ---------------------------------------------------------
# CREATE TASK
# ---------------------------------------------------------

def test_create_task(client):
    """
    A valid task should be created successfully.
    """

    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "study python",
            "description": "complete task practice",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user_id
    assert data["title"] == "study python"
    assert data["description"] == "complete task practice"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["due_date"] is None


# ---------------------------------------------------------
# INVALID TITLE
# ---------------------------------------------------------

def test_create_task_with_empty_title(client):
    """
    A task with an empty title should be rejected.
    """

    user_id = create_test_user(client)

    response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# GET USER TASKS
# ---------------------------------------------------------

def test_get_user_tasks(client):
    """
    The API should return all tasks belonging to a user.
    """

    user_id = create_test_user(client)

    client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "task one",
        },
    )

    client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "task two",
        },
    )

    response = client.get(
        f"/api/v1/tasks?user_id={user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "task two"
    assert data[1]["title"] == "task one"


# ---------------------------------------------------------
# GET SINGLE TASK
# ---------------------------------------------------------

def test_get_task(client):
    """
    A task should be retrievable using its ID.
    """

    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "read documentation",
        },
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/tasks/{task_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "read documentation"


# ---------------------------------------------------------
# GET NONEXISTENT TASK
# ---------------------------------------------------------

def test_get_nonexistent_task(client):
    """
    Requesting a task that doesn't exist should return 404.
    """

    task_id = uuid4()

    response = client.get(
        f"/api/v1/tasks/{task_id}"
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# DELETE TASK
# ---------------------------------------------------------

def test_delete_task(client):
    """
    An existing task should be deleted successfully.
    """

    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "temporary task",
        },
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/tasks/{task_id}"
    )

    assert response.status_code == 204

    # Confirm that the task no longer exists.
    get_response = client.get(
        f"/api/v1/tasks/{task_id}"
    )

    assert get_response.status_code == 404


# ---------------------------------------------------------
# DELETE NONEXISTENT TASK
# ---------------------------------------------------------

def test_delete_nonexistent_task(client):
    """
    Deleting a task that doesn't exist should return 404.
    """

    task_id = uuid4()

    response = client.delete(
        f"/api/v1/tasks/{task_id}"
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# UPDATE TASK
# ---------------------------------------------------------

def test_update_task(client):
    """
    An existing task should be updated successfully.
    """

    user_id = create_test_user(client)

    # Create the original task.
    create_response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "study python",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # Update only the priority.
    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "priority": "urgent",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Title should remain unchanged.
    assert data["title"] == "study python"

    # Priority should be updated.
    assert data["priority"] == "urgent"


# ---------------------------------------------------------
# UPDATE MULTIPLE TASK FIELDS
# ---------------------------------------------------------

def test_update_multiple_task_fields(client):
    """
    Multiple task fields should be updated in one request.
    """

    user_id = create_test_user(client)

    create_response = client.post(
        "/api/v1/tasks",
        json={
            "user_id": user_id,
            "title": "old title",
            "priority": "low",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "new title",
            "status": "completed",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "new title"
    assert data["status"] == "completed"
    assert data["priority"] == "high"


# ---------------------------------------------------------
# UPDATE NONEXISTENT TASK
# ---------------------------------------------------------

def test_update_nonexistent_task(client):
    """
    Updating a task that doesn't exist should return 404.
    """

    task_id = uuid4()

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 404



def test_update_task_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that updating a task creates a
    task_updated activity event.
    """

    # Create a task first.
    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "user_id": str(test_user.id),
            "title": "Original Task",
            "description": "Original description",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task = create_response.json()

    # Update the task.
    update_response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={
            "title": "Updated Task",
        },
    )

    assert update_response.status_code == 200

    updated_task = update_response.json()

    # Verify that the task was actually updated.
    assert updated_task["title"] == "Updated Task"

    # Check the activity event directly from the test database.
    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == task["id"],
                ActivityEvent.event_type
                == ActivityEventType.task_updated,
            )
            .first()
        )

        # An event must exist.
        assert event is not None

        # Verify that the event points to the correct task.
        assert event.entity_type == ActivityEntityType.task

        # Verify which field was updated.
        assert event.event_metadata["updated_fields"] == [
            "title"
        ]

    finally:
        db.close()



def test_complete_task_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that completing a task creates
    a task_completed activity event.
    """

    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "user_id": str(test_user.id),
            "title": "Complete Me",
            "description": "Task for completion test",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task = create_response.json()

    update_response = client.patch(
        f"/api/v1/tasks/{task['id']}",
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
                ActivityEvent.entity_id == task["id"],
                ActivityEvent.event_type
                == ActivityEventType.task_completed,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.task
        assert event.event_metadata["old_status"] == "pending"
        assert event.event_metadata["new_status"] == "completed"

    finally:
        db.close()


def test_cancel_task_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that cancelling a task creates
    a task_cancelled activity event.
    """

    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "user_id": str(test_user.id),
            "title": "Cancel Me",
            "description": "Task for cancellation test",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task = create_response.json()

    update_response = client.patch(
        f"/api/v1/tasks/{task['id']}",
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
                ActivityEvent.entity_id == task["id"],
                ActivityEvent.event_type
                == ActivityEventType.task_cancelled,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.task
        assert event.event_metadata["old_status"] == "pending"
        assert event.event_metadata["new_status"] == "cancelled"

    finally:
        db.close()



def test_reopen_task_creates_activity_event(
    client,
    test_user,
):
    """
    Verify that reopening a completed task creates
    a task_reopened activity event.
    """

    create_response = client.post(
        "/api/v1/tasks/",
        json={
            "user_id": str(test_user.id),
            "title": "Reopen Me",
            "description": "Task for reopen test",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task = create_response.json()

    # First complete the task.
    complete_response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={
            "status": "completed",
        },
    )

    assert complete_response.status_code == 200

    # Now reopen the task.
    reopen_response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={
            "status": "pending",
        },
    )

    assert reopen_response.status_code == 200
    assert reopen_response.json()["status"] == "pending"

    db = TestSessionLocal()

    try:
        event = (
            db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == test_user.id,
                ActivityEvent.entity_id == task["id"],
                ActivityEvent.event_type
                == ActivityEventType.task_reopened,
            )
            .first()
        )

        assert event is not None
        assert event.entity_type == ActivityEntityType.task
        assert event.event_metadata["old_status"] == "completed"
        assert event.event_metadata["new_status"] == "pending"

    finally:
        db.close()