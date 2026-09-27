from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """
    Provider-independent interface for the LifeOS AI layer.

    The rest of LifeOS should depend on this interface rather than
    directly depending on a specific AI provider.
    """

    @abstractmethod
    def generate_response(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate an AI response from structured LifeOS context.

        Implementations may use an external LLM, a local model,
        or a deterministic/mock provider.
        """
        raise NotImplementedError