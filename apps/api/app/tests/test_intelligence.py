from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.intelligence import IntelligenceService


def test_intelligence_pipeline():
    service = IntelligenceService.__new__(IntelligenceService)

    service.context_service = MagicMock()
    service.prioritization_service = MagicMock()
    service.recommendation_service = MagicMock()
    service.recommendation_repository = MagicMock()
    service.ai_service = MagicMock()

    service.recommendation_repository.get_active_by_signal.return_value = None

    service.recommendation_repository.create.return_value = SimpleNamespace(
        id="recommendation-id",
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=3.0,
        status="generated",
    )

    user_id = "test-user-id"

    context = {
        "generated_at": "2026-09-27T17:00:00",
        "user_id": user_id,
        "analysis": {
            "signals": [
                {
                    "type": "task_pressure",
                    "severity": "high",
                    "message": "You have a high number of pending tasks.",
                    "source": "tasks",
                    "evidence": {
                        "pending_tasks": 10,
                    },
                    "confidence": 1.0,
                }
            ]
        },
    }

    prioritized_signals = [
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

    recommendations = [
        {
            "type": "task_management",
            "title": "Reduce your pending task load",
            "message": "Review your pending tasks.",
            "reason": "You have a high number of pending tasks.",
            "source_signal": "task_pressure",
            "priority": 3.0,
        }
    ]

    ai_response = {
        "provider": "mock",
        "response": (
            "Based on your current LifeOS context, "
            "consider: Reduce your pending task load."
        ),
        "source_signal": "task_pressure",
        "confidence": 1.0,
        "recommendations": recommendations,
    }

    service.context_service.get_user_context.return_value = context

    service.prioritization_service.prioritize.return_value = (
        prioritized_signals
    )

    service.recommendation_service.generate.return_value = (
        recommendations
    )

    service.ai_service.generate_response.return_value = ai_response

    result = service.generate(user_id)

    # ---------------------------------------------------------
    # Basic intelligence response checks
    # ---------------------------------------------------------

    assert result["generated_at"] == context["generated_at"]
    assert result["user_id"] == user_id

    assert result["context"] == context
    assert result["signals"] == context["analysis"]["signals"]
    assert result["prioritized_signals"] == prioritized_signals

    # ---------------------------------------------------------
    # Persisted recommendation checks
    # ---------------------------------------------------------

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["id"] == "recommendation-id"
    assert recommendation["type"] == "task_management"
    assert recommendation["title"] == "Reduce your pending task load"
    assert recommendation["message"] == "Review your pending tasks."
    assert recommendation["reason"] == (
        "You have a high number of pending tasks."
    )
    assert recommendation["source_signal"] == "task_pressure"
    assert recommendation["priority"] == 3.0
    assert recommendation["status"] == "generated"

    # ---------------------------------------------------------
    # AI response checks
    # ---------------------------------------------------------

    assert result["ai_response"] == ai_response
    assert result["ai_response"]["provider"] == "mock"
    assert result["ai_response"]["source_signal"] == "task_pressure"
    assert result["ai_response"]["confidence"] == 1.0

    # ---------------------------------------------------------
    # Service interaction checks
    # ---------------------------------------------------------

    service.context_service.get_user_context.assert_called_once_with(
        user_id
    )

    service.prioritization_service.prioritize.assert_called_once_with(
        context["analysis"]["signals"]
    )

    service.recommendation_service.generate.assert_called_once_with(
        prioritized_signals
    )

    service.recommendation_repository.get_active_by_signal.assert_called_once_with(
        user_id=user_id,
        source_signal="task_pressure",
    )

    service.recommendation_repository.create.assert_called_once_with(
        user_id=user_id,
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=3.0,
    )

    # ---------------------------------------------------------
    # Verify exactly what was sent to the AI layer
    # ---------------------------------------------------------

    ai_input = service.ai_service.generate_response.call_args.args[0]

    assert ai_input["generated_at"] == context["generated_at"]
    assert ai_input["user_id"] == user_id
    assert ai_input["context"] == context
    assert ai_input["signals"] == context["analysis"]["signals"]
    assert ai_input["prioritized_signals"] == prioritized_signals

    assert ai_input["recommendations"] == result["recommendations"]



def test_intelligence_reuses_existing_recommendation():
    service = IntelligenceService.__new__(IntelligenceService)

    service.context_service = MagicMock()
    service.prioritization_service = MagicMock()
    service.recommendation_service = MagicMock()
    service.recommendation_repository = MagicMock()
    service.ai_service = MagicMock()

    user_id = "test-user-id"

    context = {
        "generated_at": "2026-09-27T17:00:00",
        "user_id": user_id,
        "analysis": {
            "signals": [
                {
                    "type": "task_pressure",
                    "severity": "high",
                    "message": "You have a high number of pending tasks.",
                    "source": "tasks",
                    "evidence": {
                        "pending_tasks": 10,
                    },
                    "confidence": 1.0,
                }
            ]
        },
    }

    prioritized_signals = [
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

    generated_recommendation = {
        "type": "task_management",
        "title": "Reduce your pending task load",
        "message": "Review your pending tasks.",
        "reason": "You have a high number of pending tasks.",
        "source_signal": "task_pressure",
        "priority": 3.0,
    }

    existing_recommendation = SimpleNamespace(
        id="existing-recommendation-id",
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=3.0,
        status="generated",
    )

    ai_response = {
        "provider": "mock",
        "response": (
            "Based on your current LifeOS context, "
            "consider: Reduce your pending task load."
        ),
        "source_signal": "task_pressure",
        "confidence": 1.0,
        "recommendations": [generated_recommendation],
    }

    service.context_service.get_user_context.return_value = context

    service.prioritization_service.prioritize.return_value = (
        prioritized_signals
    )

    service.recommendation_service.generate.return_value = [
        generated_recommendation
    ]

    service.recommendation_repository.get_active_by_signal.return_value = (
        existing_recommendation
    )

    service.ai_service.generate_response.return_value = ai_response

    result = service.generate(user_id)

    # ---------------------------------------------------------
    # Existing recommendation should be reused
    # ---------------------------------------------------------

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["id"] == "existing-recommendation-id"
    assert recommendation["type"] == "task_management"
    assert recommendation["title"] == "Reduce your pending task load"
    assert recommendation["message"] == "Review your pending tasks."
    assert recommendation["reason"] == (
        "You have a high number of pending tasks."
    )
    assert recommendation["source_signal"] == "task_pressure"
    assert recommendation["priority"] == 3.0
    assert recommendation["status"] == "generated"

    # ---------------------------------------------------------
    # Repository lookup should happen
    # ---------------------------------------------------------

    service.recommendation_repository.get_active_by_signal.assert_called_once_with(
        user_id=user_id,
        source_signal="task_pressure",
    )

    # ---------------------------------------------------------
    # A duplicate should NOT be created
    # ---------------------------------------------------------

    service.recommendation_repository.create.assert_not_called()

    # ---------------------------------------------------------
    # AI should receive the reused recommendation
    # ---------------------------------------------------------

    ai_input = service.ai_service.generate_response.call_args.args[0]

    assert ai_input["recommendations"] == result["recommendations"]