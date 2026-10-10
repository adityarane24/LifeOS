from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.goal import GoalStatus
from app.models.project import ProjectStatus
from app.models.task import TaskStatus
from app.services.activity_analytics import ActivityAnalyticsService
from app.services.context_analysis import ContextAnalysisService
from app.services.goal import GoalService
from app.services.habit import HabitService
from app.services.project import ProjectService
from app.services.task import TaskService
from app.services.temporal_activity import TemporalActivityService


class ContextService:
    """
    Builds a unified snapshot of the user's current LifeOS state.

    The Context Engine does not create or modify user data.
    It reads information from existing LifeOS services and
    combines it into one structured context.
    """

    def __init__(self, db: Session):
        self.db = db

        self.task_service = TaskService(db)
        self.goal_service = GoalService(db)
        self.habit_service = HabitService(db)
        self.project_service = ProjectService(db)
        self.temporal_activity_service = TemporalActivityService(db)
        self.analytics_service = ActivityAnalyticsService(db)
        self.analysis_service = ContextAnalysisService()

    def get_user_context(self, user_id: UUID) -> dict:
        """
        Build the current context for a LifeOS user.

        The context contains:
        - current tasks
        - tasks due today
        - active goals
        - goal progress
        - active habits
        - active projects
        - recent activity
        - 30-day analytics
        - derived context signals
        """

        now = datetime.now()
        start = now - timedelta(days=30)

        # -------------------------------------------------
        # TASKS
        # -------------------------------------------------

        tasks = self.task_service.get_user_tasks(user_id)

        pending_tasks = [
            task
            for task in tasks
            if task.status not in {
                TaskStatus.completed,
                TaskStatus.cancelled,
            }
        ]

        today = now.date()

        tasks_due_today = [
            task
            for task in pending_tasks
            if task.due_date is not None
            and task.due_date.date() == today
        ]

        # -------------------------------------------------
        # GOALS
        # -------------------------------------------------

        goals = self.goal_service.get_user_goals(user_id)

        active_goals = [
            goal
            for goal in goals
            if goal.status not in {
                GoalStatus.completed,
                GoalStatus.cancelled,
            }
        ]

        average_goal_progress = (
            sum(goal.progress for goal in active_goals)
            / len(active_goals)
            if active_goals
            else 0
        )

        # -------------------------------------------------
        # HABITS
        # -------------------------------------------------

        habits = self.habit_service.get_user_habits(user_id)

        active_habits = [
            habit
            for habit in habits
            if habit.is_active
        ]

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        projects = self.project_service.get_user_projects(user_id)

        active_projects = [
            project
            for project in projects
            if project.status == ProjectStatus.active
        ]

        # -------------------------------------------------
        # RECENT ACTIVITY
        # -------------------------------------------------

        recent_activity = self.temporal_activity_service.get_timeline(
            user_id=user_id,
            limit=10,
        )

        # -------------------------------------------------
        # ANALYTICS
        # -------------------------------------------------

        analytics = self.analytics_service.get_user_analytics(
            user_id=user_id,
            start=start,
            end=now,
        )

        # -------------------------------------------------
        # UNIFIED CONTEXT
        # -------------------------------------------------

        context = {
            "generated_at": now,
            "user_id": user_id,
            "tasks": {
                "total": len(tasks),
                "pending": len(pending_tasks),
                "due_today": len(tasks_due_today),
            },
            "goals": {
                "total": len(goals),
                "active": len(active_goals),
                "average_progress": round(
                    average_goal_progress,
                    2,
                ),
            },
            "habits": {
                "total": len(habits),
                "active": len(active_habits),
            },
            "projects": {
                "total": len(projects),
                "active": len(active_projects),
            },
            "recent_activity": {
    "count": len(recent_activity),
    "events": [
        {
            "id": event.id,
            "user_id": event.user_id,
            "event_type": event.event_type.value,
            "entity_type": event.entity_type.value,
            "entity_id": event.entity_id,
            "occurred_at": event.occurred_at,
            "metadata": event.event_metadata,
            "created_at": event.created_at,
        }
        for event in recent_activity
    ],
},
            "analytics": analytics,
        }

        # -------------------------------------------------
        # CONTEXT ANALYSIS
        # -------------------------------------------------

        context["analysis"] = self.analysis_service.analyze(context)

        return context