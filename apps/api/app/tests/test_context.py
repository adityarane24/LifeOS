from fastapi.testclient import TestClient

from app.services.context_analysis import ContextAnalysisService


def test_get_user_context(client: TestClient, test_user):
    response = client.get(
        "/api/v1/context",
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
    # CONTEXT SECTIONS
    # -------------------------------------------------

    assert "tasks" in data
    assert "goals" in data
    assert "habits" in data
    assert "projects" in data
    assert "recent_activity" in data
    assert "analytics" in data

    # -------------------------------------------------
    # CONTEXT ANALYSIS
    # -------------------------------------------------

    assert "analysis" in data
    assert "analyzed_at" in data["analysis"]
    assert "signal_count" in data["analysis"]
    assert "signals" in data["analysis"]

    # Empty test user should produce no signals.
    assert data["analysis"]["signal_count"] == 0
    assert data["analysis"]["signals"] == []

    # -------------------------------------------------
    # TASKS
    # -------------------------------------------------

    assert data["tasks"]["total"] == 0
    assert data["tasks"]["pending"] == 0
    assert data["tasks"]["due_today"] == 0

    # -------------------------------------------------
    # GOALS
    # -------------------------------------------------

    assert data["goals"]["total"] == 0
    assert data["goals"]["active"] == 0

    # -------------------------------------------------
    # HABITS
    # -------------------------------------------------

    assert data["habits"]["total"] == 0
    assert data["habits"]["active"] == 0

    # -------------------------------------------------
    # PROJECTS
    # -------------------------------------------------

    assert data["projects"]["total"] == 0
    assert data["projects"]["active"] == 0

    # -------------------------------------------------
    # RECENT ACTIVITY
    # -------------------------------------------------

    assert data["recent_activity"]["count"] == 0


def test_context_analysis_detects_high_task_pressure():
    service = ContextAnalysisService()

    context = {
        "tasks": {
            "pending": 10,
            "due_today": 0,
        },
        "goals": {
            "active": 0,
            "average_progress": 0,
        },
        "habits": {
            "active": 0,
        },
        "projects": {
            "active": 0,
        },
        "analytics": {
            "tasks": {
                "created": 0,
                "completion_rate": 0,
            },
            "habits": {
                "consistency_rate": 0,
            },
        },
    }

    result = service.analyze(context)

    assert result["signal_count"] == 1

    signal = result["signals"][0]

    assert signal["type"] == "task_pressure"
    assert signal["severity"] == "high"
    assert signal["message"] == (
        "You have a high number of pending tasks."
    )

    assert signal["source"] == "tasks"
    assert signal["evidence"]["pending_tasks"] == 10
    assert signal["confidence"] == 1.0