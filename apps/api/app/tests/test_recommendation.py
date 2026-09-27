from app.services.recommendation import RecommendationService


def test_generate_task_pressure_recommendation():
    service = RecommendationService()

    signals = [
        {
            "type": "task_pressure",
            "severity": "high",
            "message": "You have a high number of pending tasks.",
            "source": "tasks",
            "evidence": {
                "pending_tasks": 10,
            },
            "confidence": 1.0,
            "priority_score": 3.0,
        }
    ]

    result = service.generate(signals)

    assert len(result) == 1

    recommendation = result[0]

    assert recommendation["type"] == "task_management"
    assert recommendation["title"] == "Reduce your pending task load"
    assert recommendation["source_signal"] == "task_pressure"
    assert recommendation["priority"] == 3.0
    assert "pending tasks" in recommendation["message"]


def test_generate_multiple_recommendations():
    service = RecommendationService()

    signals = [
        {
            "type": "task_pressure",
            "severity": "high",
            "message": "You have a high number of pending tasks.",
            "source": "tasks",
            "evidence": {
                "pending_tasks": 10,
            },
            "confidence": 1.0,
            "priority_score": 3.0,
        },
        {
            "type": "low_goal_progress",
            "severity": "medium",
            "message": "Your active goals have relatively low progress.",
            "source": "goals",
            "evidence": {
                "active_goals": 2,
                "average_progress": 20,
            },
            "confidence": 1.0,
            "priority_score": 2.0,
        },
    ]

    result = service.generate(signals)

    assert len(result) == 2

    assert result[0]["source_signal"] == "task_pressure"
    assert result[1]["source_signal"] == "low_goal_progress"


def test_generate_empty_recommendations():
    service = RecommendationService()

    result = service.generate([])

    assert result == []