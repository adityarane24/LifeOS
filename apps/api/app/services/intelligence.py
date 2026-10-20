from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.recommendation import RecommendationRepository
from app.repositories.signal_state import SignalStateRepository
from app.services.ai.mock import MockAIProvider
from app.services.ai.service import AIService
from app.services.context import ContextService
from app.services.recommendation import RecommendationService
from app.services.signal_prioritization import SignalPrioritizationService


class IntelligenceService:
    """
    Application-level intelligence orchestration.

    Tracks signal lifecycles and prevents duplicate recommendations
    while a signal remains active.
    """

    def __init__(self, db: Session):
        self.db = db
        self.context_service = ContextService(db)
        self.prioritization_service = SignalPrioritizationService()
        self.recommendation_service = RecommendationService()
        self.recommendation_repository = RecommendationRepository(db)
        self.signal_state_repository = SignalStateRepository(db)
        self.ai_service = AIService(provider=MockAIProvider())

    def generate(self, user_id: UUID) -> dict[str, Any]:
        context = self.context_service.get_user_context(user_id)

        analysis = context["analysis"]
        signals = analysis["signals"]

        # Track which signals are active in the current analysis.
        current_signal_types = {
            signal["type"]
            for signal in signals
        }

        # Deactivate signals that have disappeared.
        previously_active = (
            self.signal_state_repository.get_active_by_user(user_id)
        )

        for signal_state in previously_active:
            if signal_state.signal_type not in current_signal_types:
                self.signal_state_repository.deactivate_signal(
                    user_id=user_id,
                    signal_type=signal_state.signal_type,
                )

        # Determine which signals are newly active or returning.
        newly_active_types = set()

        for signal_type in current_signal_types:
            existing_state = self.signal_state_repository.get_by_signal(
                user_id=user_id,
                signal_type=signal_type,
            )

            if existing_state is None or not existing_state.is_active:
                newly_active_types.add(signal_type)

            self.signal_state_repository.activate_signal(
                user_id=user_id,
                signal_type=signal_type,
            )

        prioritized_signals = self.prioritization_service.prioritize(
            signals
        )

        generated_recommendations = self.recommendation_service.generate(
            prioritized_signals
        )

        recommendations = []

        for recommendation_data in generated_recommendations:
            source_signal = recommendation_data.get("source_signal")

            # Do not create another recommendation for a signal
            # that was already active before this analysis.
            # Only generate a recommendation when the signal is newly active.
            if source_signal and source_signal not in newly_active_types:
                existing = self.recommendation_repository.get_active_by_signal(
                    user_id=user_id,
                    source_signal=source_signal,
                )
                if existing:
                    recommendations.append({
                        "id": existing.id, "type": existing.recommendation_type, "title": existing.title, "message": existing.message, 
                        "reason": existing.reason, "source_signal": existing.source_signal, "priority": existing.priority,
                        "status": existing.status,
                    })
            
                continue

            created = self.recommendation_repository.create(
                user_id=user_id,
                recommendation_type=recommendation_data["type"],
                title=recommendation_data["title"],
                message=recommendation_data["message"],
                reason=recommendation_data.get("reason"),
                source_signal=source_signal,
                priority=recommendation_data.get("priority", 0),
            )

            recommendations.append({
                "id": created.id,
                "type": created.recommendation_type,
                "title": created.title,
                "message": created.message,
                "reason": created.reason,
                "source_signal": created.source_signal,
                "priority": created.priority,
                "status": created.status,
            })

        # Commit signal-state changes.
        self.db.commit()

        intelligence = {
            "generated_at": context["generated_at"],
            "user_id": user_id,
            "context": context,
            "signals": signals,
            "prioritized_signals": prioritized_signals,
            "recommendations": recommendations,
        }

        ai_response = self.ai_service.generate_response(
            intelligence
        )

        intelligence["ai_response"] = ai_response

        return intelligence