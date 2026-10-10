from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.recommendation import RecommendationRepository


class RecommendationService:
    """
    Handles recommendation generation and lifecycle operations.

    Recommendation generation is deterministic and does not use AI.

    Lifecycle operations such as retrieving recommendations and updating
    their status use the recommendation repository.
    """

    def __init__(self, db: Session | None = None):
        self.repository = (
            RecommendationRepository(db)
            if db is not None
            else None
        )

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

    def get_user_recommendations(
        self,
        user_id: UUID,
    ):
        """
        Return all recommendations belonging to a user.
        """

        if self.repository is None:
            raise RuntimeError(
                "RecommendationService requires a database session "
                "for lifecycle operations."
            )

        return self.repository.get_by_user(user_id)

    def get_recommendation(
        self,
        recommendation_id: UUID,
    ):
        """
        Return a single recommendation.
        """

        if self.repository is None:
            raise RuntimeError(
                "RecommendationService requires a database session "
                "for lifecycle operations."
            )

        return self.repository.get_by_id(recommendation_id)

    def update_status(
        self,
        recommendation_id: UUID,
        status: str,
    ):
        """
        Update the lifecycle status of a recommendation.
        """

        if self.repository is None:
            raise RuntimeError(
                "RecommendationService requires a database session "
                "for lifecycle operations."
            )

        return self.repository.update_status(
            recommendation_id,
            status,
        )