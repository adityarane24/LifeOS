
def test_create_user(client):
    """
    Test that a valid user can be created successfully.
    """

    # Data that we want to send to the API.
    user_data = {
        "email": "testuser@example.com",
        "name": "Test User"
    }

    # Send a POST request to our user creation endpoint.
    response = client.post(
        "/api/v1/users",
        json=user_data
    )

    # The API should return HTTP 201 Created.
    assert response.status_code == 201

    # Convert the JSON response into a Python dictionary.
    data = response.json()

    # Verify that the API returned the correct email.
    assert data["email"] == "testuser@example.com"

    # Verify that the API returned the correct name.
    assert data["name"] == "Test User"

    # Verify that the user is active by default.
    assert data["is_active"] is True

    # Verify that an ID was generated.
    assert "id" in data


def test_create_duplicate_user(client):
    """
    Test that creating a user with an email that already exists
    is rejected by the API.
    """

    # Create the first user.
    user_data = {
        "email": "duplicate@example.com",
        "name": "First User"
    }

    response = client.post(
        "/api/v1/users",
        json=user_data
    )

    # The first user should be created successfully.
    assert response.status_code == 201

    # Try to create another user using the same email.
    duplicate_data = {
        "email": "duplicate@example.com",
        "name": "Second User"
    }

    response = client.post(
        "/api/v1/users",
        json=duplicate_data
    )

    # Our API should reject the duplicate email.
    assert response.status_code == 409

    # Verify that the response contains our error message.
    assert "already exists" in response.json()["detail"]


def test_create_user_invalid_email(client):
    """
    Test that the API rejects an invalid email address.
    """

    # Send user data containing an invalid email.
    user_data = {
        "email": "not-an-email",
        "name": "Test User"
    }

    # Send the request to the API.
    response = client.post(
        "/api/v1/users",
        json=user_data
    )

    # Pydantic validation should reject the request.
    assert response.status_code == 422


def test_create_user_missing_name(client):
    """
    Test that the API rejects a request when the name is missing.
    """

    # The email is valid, but the required name field is missing.
    user_data = {
        "email": "noname@example.com"
    }

    # Send the request to the API.
    response = client.post(
        "/api/v1/users",
        json=user_data
    )

    # Pydantic should reject the request.
    assert response.status_code == 422


def test_create_user_empty_name(client):
    """
    Test that the API rejects an empty name.
    """

    # Our schema requires the name to contain at least
    # one character.
    user_data = {
        "email": "emptyname@example.com",
        "name": ""
    }

    # Send the request to the API.
    response = client.post(
        "/api/v1/users",
        json=user_data
    )

    # The min_length=1 validation should reject it.
    assert response.status_code == 422