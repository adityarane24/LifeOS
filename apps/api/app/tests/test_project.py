def test_create_project(client, test_user):
    response = client.post(
        "/api/v1/projects",
        json={
            "user_id": str(test_user.id),
            "title": "LifeOS",
            "description": "Build my personal operating system",
            "status": "active",
            "priority": "high",
            "start_date": "2026-09-26",
            "target_date": "2026-12-31",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == str(test_user.id)
    assert data["title"] == "LifeOS"
    assert data["description"] == "Build my personal operating system"
    assert data["status"] == "active"
    assert data["priority"] == "high"
    assert data["start_date"] == "2026-09-26"
    assert data["target_date"] == "2026-12-31"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_with_defaults(client, test_user):
    response = client.post(
        "/api/v1/projects",
        json={
            "user_id": str(test_user.id),
            "title": "Python Practice",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Practice"
    assert data["status"] == "planned"
    assert data["priority"] == "medium"
    assert data["target_date"] is None


def test_get_project(client, test_user):
    create_response = client.post(
        "/api/v1/projects",
        json={
            "user_id": str(test_user.id),
            "title": "LifeOS",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/projects/{project_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["title"] == "LifeOS"


def test_get_projects_for_user(client, test_user):
    for title in ["LifeOS", "Portfolio", "Research"]:
        response = client.post(
            "/api/v1/projects",
            json={
                "user_id": str(test_user.id),
                "title": title,
            },
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/projects",
        params={"user_id": str(test_user.id)},
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 3


def test_update_project(client, test_user):
    create_response = client.post(
        "/api/v1/projects",
        json={
            "user_id": str(test_user.id),
            "title": "LifeOS",
        },
    )

    project_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "title": "LifeOS API",
            "status": "active",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "LifeOS API"
    assert data["status"] == "active"
    assert data["priority"] == "high"


def test_delete_project(client, test_user):
    create_response = client.post(
        "/api/v1/projects",
        json={
            "user_id": str(test_user.id),
            "title": "Temporary Project",
        },
    )

    project_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/projects/{project_id}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/projects/{project_id}"
    )

    assert get_response.status_code == 404


def test_get_nonexistent_project(client):
    response = client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_update_nonexistent_project(client):
    response = client.patch(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000",
        json={
            "title": "Does Not Exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_delete_nonexistent_project(client):
    response = client.delete(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"