from typing import Any


class SignalPrioritizationService:
    """
    Assigns a deterministic priority score to context signals.

    This service does not modify user data and does not use AI.
    It ranks already-detected signals so that future recommendation
    and AI layers can focus on the most important situations.
    """

    SEVERITY_WEIGHTS = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    SIGNAL_TYPE_WEIGHTS = {
        "task_pressure": 1.0,
        "due_today": 1.2,
        "low_goal_progress": 1.0,
        "habit_consistency": 0.9,
        "task_completion": 0.9,
    }

    def prioritize(
        self,
        signals: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        prioritized_signals = []

        for signal in signals:
            severity_weight = self.SEVERITY_WEIGHTS.get(
                signal.get("severity", "low"),
                1,
            )

            type_weight = self.SIGNAL_TYPE_WEIGHTS.get(
                signal.get("type", ""),
                0.8,
            )

            confidence = signal.get("confidence", 1.0)

            score = severity_weight * type_weight * confidence

            prioritized_signal = {
                **signal,
                "priority_score": round(score, 2),
            }

            prioritized_signals.append(prioritized_signal)

        prioritized_signals.sort(
            key=lambda signal: signal["priority_score"],
            reverse=True,
        )

        return prioritized_signals