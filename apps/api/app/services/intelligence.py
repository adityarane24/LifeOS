from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.ai.mock import MockAIProvider
from app.services.ai.service import AIService
from app.services.context import ContextService
from app.services.recommendation import RecommendationService
from app.services.signal_prioritization import SignalPrioritizationService


class IntelligenceService:
    """
    Application-level intelligence orchestration.

    This service builds LifeOS context, analyzes signals,
    prioritizes them, generates recommendations, and then
    passes a controlled context to the AI layer.
    """

    def __init__(self, db: Session):
        self.context_service = ContextService(db)
        self.prioritization_service = SignalPrioritizationService()
        self.recommendation_service = RecommendationService()

        self.ai_service = AIService(
            provider=MockAIProvider()
        )

    def generate(self, user_id: UUID) -> dict[str, Any]:
        context = self.context_service.get_user_context(user_id)

        analysis = context["analysis"]
        signals = analysis["signals"]

        prioritized_signals = self.prioritization_service.prioritize(
            signals
        )

        recommendations = self.recommendation_service.generate(
            prioritized_signals
        )

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