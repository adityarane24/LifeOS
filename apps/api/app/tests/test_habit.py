from datetime import date

from app.models.habit import HabitFrequency


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

    # Create a habit.
    habit_response = client.post(
        "/api/v1/habits",
        json={
            "user_id": str(test_user.id),
            "title": "Study Python",
            "start_date": "2026-09-10",
        },
    )

    assert habit_response.status_code == 201

    habit_id = habit_response.json()["id"]

    # Add three completed days.
    for completion_date in [
        "2026-09-13",
        "2026-09-14",
        "2026-09-15",
    ]:
        response = client.post(
            f"/api/v1/habits/{habit_id}/completions",
            json={
                "completion_date": completion_date,
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