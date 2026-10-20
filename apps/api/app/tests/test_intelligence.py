from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.intelligence import IntelligenceService


def create_test_service():
    """Create an IntelligenceService with mocked dependencies."""

    service = IntelligenceService.__new__(IntelligenceService)

    service.context_service = MagicMock()
    service.prioritization_service = MagicMock()
    service.recommendation_service = MagicMock()
    service.recommendation_repository = MagicMock()
    service.signal_state_repository = MagicMock()
    service.db = MagicMock()
    service.ai_service = MagicMock()

    service.signal_state_repository.get_active_by_user.return_value = []
    service.signal_state_repository.get_by_signal.return_value = None

    service.recommendation_repository.get_active_by_signal.return_value = None

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

    service.ai_service.generate_response.return_value = ai_response

    return (
        service,
        user_id,
        context,
        prioritized_signals,
        generated_recommendation,
        ai_response,
    )


def create_saved_recommendation(status="generated"):
    """Create a mock of a recommendation already saved in the database."""

    return SimpleNamespace(
        id="existing-recommendation-id",
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=3.0,
        status=status,
    )


def test_intelligence_pipeline():
    (
        service,
        user_id,
        context,
        prioritized_signals,
        generated_recommendation,
        ai_response,
    ) = create_test_service()

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

    result = service.generate(user_id)

    # Basic intelligence response checks.

    assert result["generated_at"] == context["generated_at"]
    assert result["user_id"] == user_id
    assert result["context"] == context
    assert result["signals"] == context["analysis"]["signals"]
    assert result["prioritized_signals"] == prioritized_signals

    # Newly active signals should create a recommendation.

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

    service.recommendation_repository.create.assert_called_once_with(
        user_id=user_id,
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=3.0,
    )

    # A newly active signal should not require an existing recommendation.

    service.recommendation_repository.get_active_by_signal.assert_not_called()

    # Signal state should be tracked.

    service.signal_state_repository.activate_signal.assert_called_once_with(
        user_id=user_id,
        signal_type="task_pressure",
    )

    service.db.commit.assert_called_once()

    # Verify the AI response.

    assert result["ai_response"] == ai_response

    ai_input = service.ai_service.generate_response.call_args.args[0]

    assert ai_input["generated_at"] == context["generated_at"]
    assert ai_input["user_id"] == user_id
    assert ai_input["context"] == context
    assert ai_input["signals"] == context["analysis"]["signals"]
    assert ai_input["prioritized_signals"] == prioritized_signals
    assert ai_input["recommendations"] == result["recommendations"]


def test_intelligence_reuses_existing_recommendation():
    (
        service,
        user_id,
        context,
        prioritized_signals,
        generated_recommendation,
        ai_response,
    ) = create_test_service()

    # Simulate a signal that was already active before this analysis.

    active_signal = SimpleNamespace(
        signal_type="task_pressure",
        is_active=True,
    )

    service.signal_state_repository.get_active_by_user.return_value = [
        active_signal
    ]

    service.signal_state_repository.get_by_signal.return_value = active_signal

    existing_recommendation = create_saved_recommendation()

    service.recommendation_repository.get_active_by_signal.return_value = (
        existing_recommendation
    )

    result = service.generate(user_id)

    # The existing recommendation should be reused.

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["id"] == "existing-recommendation-id"
    assert recommendation["type"] == "task_management"
    assert recommendation["title"] == "Reduce your pending task load"
    assert recommendation["message"] == "Review your pending tasks."
    assert recommendation["source_signal"] == "task_pressure"
    assert recommendation["status"] == "generated"

    service.recommendation_repository.get_active_by_signal.assert_called_once_with(
        user_id=user_id,
        source_signal="task_pressure",
    )

    # No duplicate should be created.

    service.recommendation_repository.create.assert_not_called()

    # AI should receive the reused recommendation.

    ai_input = service.ai_service.generate_response.call_args.args[0]

    assert ai_input["recommendations"] == result["recommendations"]


@pytest.mark.parametrize("previous_status", ["accepted", "dismissed"])
def test_active_signal_does_not_recreate_accepted_or_dismissed_recommendation(
    previous_status,
):
    (
        service,
        user_id,
        context,
        prioritized_signals,
        generated_recommendation,
        ai_response,
    ) = create_test_service()

    # The signal is still active.

    active_signal = SimpleNamespace(
        signal_type="task_pressure",
        is_active=True,
    )

    service.signal_state_repository.get_active_by_user.return_value = [
        active_signal
    ]

    service.signal_state_repository.get_by_signal.return_value = active_signal

    # The previous recommendation was accepted or dismissed.
    # It is therefore not returned by get_active_by_signal().

    service.recommendation_repository.get_active_by_signal.return_value = None

    result = service.generate(user_id)

    # The service must not recreate the recommendation while the signal
    # remains active.

    assert result["recommendations"] == []

    service.recommendation_repository.create.assert_not_called()

    service.recommendation_repository.get_active_by_signal.assert_called_once_with(
        user_id=user_id,
        source_signal="task_pressure",
    )




def test_signal_returning_after_disappearing_creates_new_recommendation():
    (
        service,
        user_id,
        context,
        prioritized_signals,
        generated_recommendation,
        ai_response,
    ) = create_test_service()

    # First analysis: the signal is active.
    service.recommendation_repository.create.return_value = (
        create_saved_recommendation()
    )

    service.generate(user_id)

    service.recommendation_repository.create.assert_called_once()

    # Second analysis: the signal disappears.
    context["analysis"]["signals"] = []
    service.prioritization_service.prioritize.return_value = []

    service.signal_state_repository.get_active_by_user.return_value = [
        SimpleNamespace(
            signal_type="task_pressure",
            is_active=True,
        )
    ]

    service.recommendation_service.generate.return_value = []

    service.generate(user_id)

    service.signal_state_repository.deactivate_signal.assert_called_once_with(
        user_id=user_id,
        signal_type="task_pressure",
    )

    # Third analysis: the same signal returns.
    context["analysis"]["signals"] = [
        {
            "type": "task_pressure",
            "severity": "high",
            "message": "You have a high number of pending tasks.",
            "source": "tasks",
            "evidence": {"pending_tasks": 10},
            "confidence": 1.0,
        }
    ]

    service.prioritization_service.prioritize.return_value = (
        prioritized_signals
    )
    service.recommendation_service.generate.return_value = [
        generated_recommendation
    ]

    # The previous state is now inactive, so the signal is newly active.
    service.signal_state_repository.get_active_by_user.return_value = []
    service.signal_state_repository.get_by_signal.return_value = (
        SimpleNamespace(
            signal_type="task_pressure",
            is_active=False,
        )
    )

    service.recommendation_repository.create.return_value = (
        SimpleNamespace(
            id="new-recommendation-id",
            recommendation_type="task_management",
            title="Reduce your pending task load",
            message="Review your pending tasks.",
            reason="You have a high number of pending tasks.",
            source_signal="task_pressure",
            priority=3.0,
            status="generated",
        )
    )

    result = service.generate(user_id)

    assert len(result["recommendations"]) == 1
    assert result["recommendations"][0]["id"] == "new-recommendation-id"
    assert service.recommendation_repository.create.call_count == 2
