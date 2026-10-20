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
                evidence = signal.get("evidence", {})
                pending_tasks = evidence.get("pending_tasks")

                if pending_tasks is not None:
                    message = (
                        f"You have {pending_tasks} pending tasks. "
                        "Review them and focus on the highest-priority "
                        "work before adding new tasks."
                    )
                else:
                    message = (
                        "Review your pending tasks and focus on the "
                        "highest-priority work before adding new tasks."
                    )

                recommendations.append(
                    {
                        "type": "task_management",
                        "title": "Reduce your pending task load",
                        "message": message,
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
                evidence = signal.get("evidence", {})
                active_goals = evidence.get("active_goals")
                average_progress = evidence.get("average_progress")

                if (
                    active_goals is not None
                    and average_progress is not None
                ):
                    message = (
                        f"You have {active_goals} active goals with "
                        f"an average progress of {average_progress}%. "
                        "Choose one goal and define a small next action "
                        "to move it forward."
                    )
                else:
                    message = (
                        "Choose one active goal and define a small "
                        "next action to move it forward."
                    )

                recommendations.append(
                    {
                        "type": "goal_management",
                        "title": "Review your goal progress",
                        "message": message,
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "habit_consistency":
                evidence = signal.get("evidence", {})
                active_habits = evidence.get("active_habits")
                consistency_rate = evidence.get("consistency_rate")

                if (
                    active_habits is not None
                    and consistency_rate is not None
                ):
                    message = (
                        f"You have {active_habits} active habits "
                        f"with a consistency rate of {consistency_rate}%. "
                        "Focus on maintaining one important habit "
                        "consistently before adding new habits."
                    )
                else:
                    message = (
                        "Focus on maintaining your most important habit "
                        "consistently before adding new habits."
                    )

                recommendations.append(
                    {
                        "type": "habit_management",
                        "title": "Rebuild habit consistency",
                        "message": message,
                        "reason": signal.get("message"),
                        "source_signal": signal_type,
                        "priority": signal.get("priority_score", 0),
                    }
                )

            elif signal_type == "task_completion":
                evidence = signal.get("evidence", {})
                created_tasks = evidence.get("created_tasks")
                completion_rate = evidence.get("completion_rate")

                if (
                    created_tasks is not None
                    and completion_rate is not None
                ):
                    message = (
                        f"You created {created_tasks} tasks, and your "
                        f"completion rate is {completion_rate}%. "
                        "Review unfinished tasks and identify why they "
                        "are not being completed."
                    )
                else:
                    message = (
                        "Review unfinished tasks and identify why they "
                        "are not being completed."
                    )

                recommendations.append(
                    {
                        "type": "task_management",
                        "title": "Improve task completion",
                        "message": message,
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