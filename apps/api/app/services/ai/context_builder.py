from typing import Any


class AIContextBuilder:
    """
    Builds a controlled context for the AI layer.

    The AI should not receive unrestricted LifeOS data.
    This builder selects only the information required for
    reasoning and recommendation generation.
    """

    def build(
        self,
        intelligence: dict[str, Any],
    ) -> dict[str, Any]:
        context = intelligence.get("context", {})
        analysis = context.get("analysis", {})

        return {
            "current_state": {
                "tasks": context.get("tasks", {}),
                "goals": context.get("goals", {}),
                "habits": context.get("habits", {}),
                "projects": context.get("projects", {}),
            },
            "signals": analysis.get("signals", []),
            "prioritized_signals": intelligence.get(
                "prioritized_signals",
                [],
            ),
            "recommendations": intelligence.get(
                "recommendations",
                [],
            ),
        }