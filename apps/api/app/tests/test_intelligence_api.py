from fastapi.testclient import TestClient


def test_get_intelligence(client: TestClient, test_user):
    response = client.get(
        "/api/v1/intelligence",
        params={"user_id": str(test_user.id)},
    )

    assert response.status_code == 200

    data = response.json()

    # -------------------------------------------------
    # BASIC RESPONSE
    # -------------------------------------------------

    assert data["user_id"] == str(test_user.id)
    assert "generated_at" in data

    # -------------------------------------------------
    # INTELLIGENCE SECTIONS
    # -------------------------------------------------

    assert "signals" in data
    assert "prioritized_signals" in data
    assert "recommendations" in data

    # Empty test user should produce no intelligence signals.
    assert data["signals"] == []
    assert data["prioritized_signals"] == []
    assert data["recommendations"] == []