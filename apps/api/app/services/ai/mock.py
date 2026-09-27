from typing import Any

from app.schemas.ai import AIResponse
from app.services.ai.provider import AIProvider


class MockAIProvider(AIProvider):
    def generate_response(self, context: dict[str, Any]) -> dict[str, Any]:
        recommendations = context.get("recommendations", [])

        if recommendations:
            first_recommendation = recommendations[0]

            return AIResponse(
                provider="mock",
                response=(
                    "Based on your current LifeOS context, "
                    f"consider: {first_recommendation['title']}."
                ),
                source_signal=first_recommendation.get("source_signal"),
                confidence=1.0,
                recommendations=recommendations,
            ).model_dump()

        return AIResponse(
            provider="mock",
            response=(
                "Your current LifeOS context does not indicate "
                "an immediate recommendation."
            ),
            source_signal=None,
            confidence=1.0,
            recommendations=[],
        ).model_dump()