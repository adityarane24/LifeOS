from datetime import date, timedelta

from app.models.habit import Habit, HabitCompletion


class HabitAnalytics:
    """
    Calculates useful metrics from a habit's
    schedule and completion history.
    """

    @staticmethod
    def is_scheduled(
        habit: Habit,
        current_date: date,
    ) -> bool:
        """
        Check whether a habit is scheduled on a
        particular date.
        """

        # A date before the habit started is not scheduled.
        if current_date < habit.start_date:
            return False

        # Daily habits are scheduled every day.
        if habit.frequency.value == "daily":
            return True

        # Weekly habits use days_of_week.
        if habit.frequency.value == "weekly":

            if not habit.days_of_week:
                return False

            weekday = current_date.strftime("%A").lower()

            return weekday in habit.days_of_week

        return False

    @staticmethod
    def calculate_current_streak(
        habit: Habit,
        completions: list[HabitCompletion],
        today: date | None = None,
    ) -> int:
        """
        Calculate the current consecutive completion streak.
        """

        if today is None:
            today = date.today()

        completed_dates = {
            completion.completion_date
            for completion in completions
            if completion.completed
        }

        streak = 0
        current_date = today

        while current_date >= habit.start_date:

            # Ignore days on which the habit was not scheduled.
            if not HabitAnalytics.is_scheduled(
                habit,
                current_date,
            ):
                current_date -= timedelta(days=1)
                continue

            # Stop when a scheduled day was missed.
            if current_date not in completed_dates:
                break

            streak += 1
            current_date -= timedelta(days=1)

        return streak

    @staticmethod
    def calculate_longest_streak(
        habit: Habit,
        completions: list[HabitCompletion],
    ) -> int:
        """
        Calculate the longest consecutive completion streak.
        """

        completed_dates = {
            completion.completion_date
            for completion in completions
            if completion.completed
        }

        if not completed_dates:
            return 0

        first_date = min(completed_dates)
        last_date = max(completed_dates)

        longest_streak = 0
        current_streak = 0

        current_date = first_date

        while current_date <= last_date:

            if not HabitAnalytics.is_scheduled(
                habit,
                current_date,
            ):
                current_date += timedelta(days=1)
                continue

            if current_date in completed_dates:
                current_streak += 1

                longest_streak = max(
                    longest_streak,
                    current_streak,
                )

            else:
                current_streak = 0

            current_date += timedelta(days=1)

        return longest_streak


    @staticmethod
    def calculate_completion_rate(
        habit: Habit,
        completions: list[HabitCompletion],
        today: date | None = None,
    ) -> float:
        """
        Calculate the percentage of scheduled days
        on which the habit was completed.
        """

        if today is None:
            today = date.today()

        completed_dates = {
            completion.completion_date
            for completion in completions
            if completion.completed
        }

        scheduled_days = 0
        completed_days = 0

        current_date = habit.start_date

        while current_date <= today:

            if HabitAnalytics.is_scheduled(
                habit,
                current_date,
            ):
                scheduled_days += 1

                if current_date in completed_dates:
                    completed_days += 1

            current_date += timedelta(days=1)

        if scheduled_days == 0:
            return 0.0

        return round(
            (completed_days / scheduled_days) * 100,
            2,
        )