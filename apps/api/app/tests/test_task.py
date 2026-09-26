# ---------------------------------------------------------
# Task API Tests
# ---------------------------------------------------------
#
# These tests verify the Task API from the HTTP layer
# all the way to the PostgreSQL test database.


from uuid import uuid4


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