from typing import Any


class RecommendationService:
    """
    Converts prioritized context signals into actionable recommendations.

    This service does not modify user data and does not use AI.
    Every recommendation is generated from an explicit signal rule.
    """

    def generate(
        self,
        prioritized_signals: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        recommendations = []

        for signal in prioritized_signals:
            signal_type = signal.get("type")

            if signal_type == "task_pressure":
                recommendations.append(
                    {
                        "type": "task_management",
                        "title": "Reduce your pending task load",
                        "message": (
                            "Review your pending tasks and focus on the "
                            "highest-priority work before adding new tasks."
                        ),
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "due_today":
                recommendations.append(
                    {
                        "type": "task_management",
                        "title": "Focus on today's deadlines",
                        "message": (
                            "Review the tasks due today and complete or "
                            "reschedule them before their deadlines."
                        ),
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "low_goal_progress":
                recommendations.append(
                    {
                        "type": "goal_management",
                        "title": "Review your goal progress",
                        "message": (
                            "Choose one active goal and define a small "
                            "next action to move it forward."
                        ),
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "habit_consistency":
                recommendations.append(
                    {
                        "type": "habit_management",
                        "title": "Rebuild habit consistency",
                        "message": (
                            "Focus on maintaining your most important habit "
                            "consistently before adding new habits."
                        ),
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "task_completion":
                recommendations.append(
                    {
                        "type": "task_management",
                        "title": "Improve task completion",
                        "message": (
                            "Review unfinished tasks and identify why they "
                            "are not being completed."
                        ),
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

        return recommendations