from unittest.mock import MagicMock

from app.services.intelligence import IntelligenceService


def test_intelligence_pipeline():
    service = IntelligenceService.__new__(IntelligenceService)

    service.context_service = MagicMock()
    service.prioritization_service = MagicMock()
    service.recommendation_service = MagicMock()
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

    assert result["generated_at"] == context["generated_at"]
    assert result["user_id"] == user_id

    assert result["context"] == context
    assert result["signals"] == context["analysis"]["signals"]
    assert result["prioritized_signals"] == prioritized_signals
    assert result["recommendations"] == recommendations

    assert result["ai_response"] == ai_response
    assert result["ai_response"]["provider"] == "mock"
    assert result["ai_response"]["source_signal"] == "task_pressure"
    assert result["ai_response"]["confidence"] == 1.0

    service.context_service.get_user_context.assert_called_once_with(
        user_id
    )

    service.prioritization_service.prioritize.assert_called_once_with(
        context["analysis"]["signals"]
    )

    service.recommendation_service.generate.assert_called_once_with(
        prioritized_signals
    )


    ai_input = service.ai_service.generate_response.call_args.args[0]

    assert ai_input["generated_at"] == context["generated_at"]
    assert ai_input["user_id"] == user_id
    assert ai_input["context"] == context
    assert ai_input["signals"] == context["analysis"]["signals"]
    assert ai_input["prioritized_signals"] == prioritized_signals
    assert ai_input["recommendations"] == recommendations

    