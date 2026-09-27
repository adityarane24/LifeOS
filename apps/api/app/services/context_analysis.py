from datetime import datetime
from typing import Any


class ContextAnalysisService:
    """
    Analyzes the unified LifeOS context and extracts
    structured, evidence-based signals.

    This service does not modify user data.
    It only interprets the context produced by ContextService.
    """

    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        signals = []

        tasks = context["tasks"]
        goals = context["goals"]
        habits = context["habits"]
        analytics = context["analytics"]

        # -------------------------------------------------
        # TASK PRESSURE
        # -------------------------------------------------

        pending_tasks = tasks["pending"]

        if pending_tasks >= 10:
            signals.append(
                {
                    "type": "task_pressure",
                    "severity": "high",
                    "message": "You have a high number of pending tasks.",
                    "source": "tasks",
                    "evidence": {
                        "pending_tasks": pending_tasks,
                    },
                    "confidence": 1.0,
                }
            )

        elif pending_tasks >= 5:
            signals.append(
                {
                    "type": "task_pressure",
                    "severity": "medium",
                    "message": "You have several pending tasks.",
                    "source": "tasks",
                    "evidence": {
                        "pending_tasks": pending_tasks,
                    },
                    "confidence": 1.0,
                }
            )

        # -------------------------------------------------
        # TASKS DUE TODAY
        # -------------------------------------------------

        due_today = tasks["due_today"]

        if due_today > 0:
            signals.append(
                {
                    "type": "due_today",
                    "severity": "medium",
                    "message": f"You have {due_today} task(s) due today.",
                    "source": "tasks",
                    "evidence": {
                        "tasks_due_today": due_today,
                    },
                    "confidence": 1.0,
                }
            )

        # -------------------------------------------------
        # GOAL PROGRESS
        # -------------------------------------------------

        average_goal_progress = goals["average_progress"]

        if goals["active"] > 0 and average_goal_progress < 30:
            signals.append(
                {
                    "type": "low_goal_progress",
                    "severity": "medium",
                    "message": "Your active goals have relatively low progress.",
                    "source": "goals",
                    "evidence": {
                        "active_goals": goals["active"],
                        "average_progress": average_goal_progress,
                    },
                    "confidence": 1.0,
                }
            )

        # -------------------------------------------------
        # HABIT CONSISTENCY
        # -------------------------------------------------

        habit_analytics = analytics.get("habits", {})
        consistency_rate = habit_analytics.get("consistency_rate", 0)

        if habits["active"] > 0 and consistency_rate < 50:
            signals.append(
                {
                    "type": "habit_consistency",
                    "severity": "medium",
                    "message": "Your recent habit consistency is below 50%.",
                    "source": "habits",
                    "evidence": {
                        "active_habits": habits["active"],
                        "consistency_rate": consistency_rate,
                    },
                    "confidence": 1.0,
                }
            )

        # -------------------------------------------------
        # TASK COMPLETION
        # -------------------------------------------------

        task_analytics = analytics.get("tasks", {})
        completion_rate = task_analytics.get("completion_rate", 0)
        created_tasks = task_analytics.get("created", 0)

        if created_tasks > 0 and completion_rate < 50:
            signals.append(
                {
                    "type": "task_completion",
                    "severity": "medium",
                    "message": "Your recent task completion rate is below 50%.",
                    "source": "analytics",
                    "evidence": {
                        "created_tasks": created_tasks,
                        "completion_rate": completion_rate,
                    },
                    "confidence": 1.0,
                }
            )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return {
            "analyzed_at": datetime.now(),
            "signal_count": len(signals),
            "signals": signals,
        }