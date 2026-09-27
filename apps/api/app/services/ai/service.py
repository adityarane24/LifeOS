from typing import Any

from app.services.ai.context_builder import AIContextBuilder
from app.services.ai.provider import AIProvider


class AIService:
    """
    Application-level AI service.

    The service builds a controlled AI context before passing
    information to the selected AI provider.

    It does not access the database directly.
    """

    def __init__(
        self,
        provider: AIProvider,
        context_builder: AIContextBuilder | None = None,
    ):
        self.provider = provider
        self.context_builder = context_builder or AIContextBuilder()

    def generate_response(
        self,
        intelligence: dict[str, Any],
    ) -> dict[str, Any]:
        ai_context = self.context_builder.build(intelligence)

        return self.provider.generate_response(ai_context)