from app.services.ai.mock import MockAIProvider
from app.services.ai.service import AIService


def test_mock_ai_provider_with_recommendation():
    provider = MockAIProvider()

    context = {
        "recommendations": [
            {
                "title": "Reduce your pending task load",
                "source_signal": "task_pressure",
            }
        ]
    }

    result = provider.generate_response(context)

    assert result["provider"] == "mock"
    assert "Reduce your pending task load" in result["response"]
    assert result["source_signal"] == "task_pressure"
    assert result["confidence"] == 1.0
    assert len(result["recommendations"]) == 1


def test_mock_ai_provider_without_recommendation():
    provider = MockAIProvider()

    context = {
        "recommendations": []
    }

    result = provider.generate_response(context)

    assert result["provider"] == "mock"
    assert result["source_signal"] is None
    assert result["confidence"] == 1.0
    assert result["recommendations"] == []


def test_ai_service_uses_controlled_context():
    provider = MockAIProvider()
    service = AIService(provider)

    intelligence = {
        "context": {
            "tasks": {
                "pending": 7,
                "due_today": 2,
            },
            "goals": {
                "active": 3,
            },
            "habits": {
                "active": 4,
            },
            "projects": {
                "active": 2,
            },
            "recent_activity": {
                "events": ["private-internal-data"],
            },
            "analytics": {
                "internal": "analytics-data",
            },
            "analysis": {
                "signals": [],
            },
        },
        "prioritized_signals": [],
        "recommendations": [
            {
                "title": "Review your goal progress",
                "source_signal": "low_goal_progress",
            }
        ],
    }

    result = service.generate_response(intelligence)

    assert result["provider"] == "mock"
    assert "Review your goal progress" in result["response"]
    assert result["source_signal"] == "low_goal_progress"
    assert result["confidence"] == 1.0
    assert len(result["recommendations"]) == 1