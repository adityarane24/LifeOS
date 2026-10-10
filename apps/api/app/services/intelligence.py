from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.recommendation import RecommendationRepository
from app.services.ai.mock import MockAIProvider
from app.services.ai.service import AIService
from app.services.context import ContextService
from app.services.recommendation import RecommendationService
from app.services.signal_prioritization import SignalPrioritizationService


class IntelligenceService:
    """
    Application-level intelligence orchestration.

    This service builds LifeOS context, analyzes signals,
    prioritizes them, generates recommendations, persists
    them when necessary, and then passes a controlled
    context to the AI layer.
    """

    def __init__(self, db: Session):
        self.context_service = ContextService(db)
        self.prioritization_service = SignalPrioritizationService()
        self.recommendation_service = RecommendationService()
        self.recommendation_repository = RecommendationRepository(db)
        self.ai_service = AIService(provider=MockAIProvider())

    def generate(self, user_id: UUID) -> dict[str, Any]:
        context = self.context_service.get_user_context(user_id)

        analysis = context["analysis"]
        signals = analysis["signals"]

        prioritized_signals = self.prioritization_service.prioritize(
            signals
        )

        generated_recommendations = self.recommendation_service.generate(
            prioritized_signals
        )

        recommendations = []

        for recommendation_data in generated_recommendations:
            source_signal = recommendation_data.get("source_signal")

            existing = None

            if source_signal:
                existing = self.recommendation_repository.get_active_by_signal(
                    user_id=user_id,
                    source_signal=source_signal,
                )

            if existing:
                recommendations.append({
                    "id": existing.id,
                    "type": existing.recommendation_type,
                    "title": existing.title,
                    "message": existing.message,
                    "reason": existing.reason,
                    "source_signal": existing.source_signal,
                    "priority": existing.priority,
                    "status": existing.status,
                })
            else:
                created = self.recommendation_repository.create(
                    user_id=user_id,
                    recommendation_type=recommendation_data["type"],
                    title=recommendation_data["title"],
                    message=recommendation_data["message"],
                    reason=recommendation_data.get("reason"),
                    source_signal=recommendation_data.get("source_signal"),
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