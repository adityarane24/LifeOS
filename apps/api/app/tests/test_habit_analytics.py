from datetime import date

from app.models.habit import (
    Habit,
    HabitCompletion,
    HabitFrequency,
)
from app.services.habit_analytics import HabitAnalytics


def create_habit(
    frequency=HabitFrequency.daily,
    days_of_week=None,
    start_date=date(2026, 9, 1),
):
    """
    Create a Habit object for testing.

    This does not save anything to PostgreSQL.
    """

    return Habit(
        user_id="00000000-0000-0000-0000-000000000001",
        title="Test Habit",
        frequency=frequency,
        days_of_week=days_of_week,
        target=1,
        unit="times",
        start_date=start_date,
        is_active=True,
    )


def create_completion(
    completion_date,
    completed=True,
):
    """
    Create a completion object for testing.

    This also does not save anything to PostgreSQL.
    """

    return HabitCompletion(
        habit_id="00000000-0000-0000-0000-000000000002",
        completion_date=completion_date,
        value=1,
        completed=completed,
    )


def test_daily_habit_current_streak():
    habit = create_habit()

    completions = [
        create_completion(date(2026, 9, 13)),
        create_completion(date(2026, 9, 14)),
        create_completion(date(2026, 9, 15)),
    ]

    streak = HabitAnalytics.calculate_current_streak(
        habit,
        completions,
        today=date(2026, 9, 15),
    )

    assert streak == 3


def test_daily_habit_streak_stops_at_missed_day():
    habit = create_habit()

    completions = [
        create_completion(date(2026, 9, 12)),
        create_completion(date(2026, 9, 13)),
        create_completion(
            date(2026, 9, 14),
            completed=False,
        ),
        create_completion(date(2026, 9, 15)),
    ]

    streak = HabitAnalytics.calculate_current_streak(
        habit,
        completions,
        today=date(2026, 9, 15),
    )

    assert streak == 1


def test_daily_habit_longest_streak():
    habit = create_habit()

    completions = [
        create_completion(date(2026, 9, 1)),
        create_completion(date(2026, 9, 2)),
        create_completion(date(2026, 9, 3)),
        create_completion(date(2026, 9, 5)),
        create_completion(date(2026, 9, 6)),
    ]

    streak = HabitAnalytics.calculate_longest_streak(
        habit,
        completions,
    )

    assert streak == 3


def test_no_completions():
    habit = create_habit()

    current_streak = HabitAnalytics.calculate_current_streak(
        habit,
        [],
        today=date(2026, 9, 15),
    )

    longest_streak = HabitAnalytics.calculate_longest_streak(
        habit,
        [],
    )

    assert current_streak == 0
    assert longest_streak == 0


def test_date_before_habit_start_is_not_scheduled():
    habit = create_habit(
        start_date=date(2026, 9, 10),
    )

    assert (
        HabitAnalytics.is_scheduled(
            habit,
            date(2026, 9, 9),
        )
        is False
    )


def test_daily_habit_is_scheduled():
    habit = create_habit()

    assert (
        HabitAnalytics.is_scheduled(
            habit,
            date(2026, 9, 15),
        )
        is True
    )


def test_weekly_habit_only_scheduled_days_count():
    habit = create_habit(
        frequency=HabitFrequency.weekly,
        days_of_week=[
            "monday",
            "wednesday",
            "friday",
        ],
    )

    # 15 September 2026 is Tuesday.
    assert (
        HabitAnalytics.is_scheduled(
            habit,
            date(2026, 9, 15),
        )
        is False
    )

    # 14 September 2026 is Monday.
    assert (
        HabitAnalytics.is_scheduled(
            habit,
            date(2026, 9, 14),
        )
        is True
    )


def test_weekly_habit_current_streak():
    habit = create_habit(
        frequency=HabitFrequency.weekly,
        days_of_week=[
            "monday",
            "wednesday",
            "friday",
        ],
    )

    completions = [
        create_completion(date(2026, 9, 9)),   # Wednesday
        create_completion(date(2026, 9, 11)),  # Friday
        create_completion(date(2026, 9, 14)),  # Monday
    ]

    streak = HabitAnalytics.calculate_current_streak(
        habit,
        completions,
        today=date(2026, 9, 15),  # Tuesday
    )

    assert streak == 3


def test_daily_habit_completion_rate():
    habit = create_habit(
        start_date=date(2026, 9, 10),
    )

    completions = [
        create_completion(date(2026, 9, 10)),
        create_completion(date(2026, 9, 11)),
        create_completion(
            date(2026, 9, 12),
            completed=False,
        ),
        create_completion(date(2026, 9, 13)),
        create_completion(
            date(2026, 9, 14),
            completed=False,
        ),
        create_completion(date(2026, 9, 15)),
    ]

    rate = HabitAnalytics.calculate_completion_rate(
        habit,
        completions,
        today=date(2026, 9, 15),
    )

    assert rate == 66.67


def test_weekly_habit_completion_rate():
    habit = create_habit(
        frequency=HabitFrequency.weekly,
        days_of_week=[
            "monday",
            "wednesday",
            "friday",
        ],
        start_date=date(2026, 9, 7),
    )

    completions = [
        create_completion(date(2026, 9, 7)),   # Monday
        create_completion(date(2026, 9, 9)),   # Wednesday
        create_completion(
            date(2026, 9, 11),
            completed=False,
        ),  # Friday
        create_completion(date(2026, 9, 14)),  # Monday
    ]

    rate = HabitAnalytics.calculate_completion_rate(
        habit,
        completions,
        today=date(2026, 9, 15),
    )

    assert rate == 75.0


def test_future_dates_do_not_count():
    habit = create_habit(
        start_date=date(2026, 9, 10),
    )

    completions = [
        create_completion(date(2026, 9, 10)),
        create_completion(date(2026, 9, 11)),
    ]

    rate = HabitAnalytics.calculate_completion_rate(
        habit,
        completions,
        today=date(2026, 9, 11),
    )

    assert rate == 100.0