import uuid
from app.repositories.recommendation import RecommendationRepository
from app.tests.conftest import TestSessionLocal


def test_create_recommendation(test_user):
    db = TestSessionLocal()

    repository = RecommendationRepository(db)

    recommendation = repository.create(
        user_id=test_user.id,
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks and focus on the highest-priority work.",
        reason="You have a high number of pending tasks.",
        source_signal="task_pressure",
        priority=0.9,
    )

    assert recommendation.id is not None
    assert recommendation.user_id == test_user.id
    assert recommendation.recommendation_type == "task_management"
    assert recommendation.title == "Reduce your pending task load"
    assert recommendation.status == "generated"

    db.close()


def test_get_recommendation_by_id(test_user):
    db = TestSessionLocal()

    repository = RecommendationRepository(db)

    created = repository.create(
        user_id=test_user.id,
        recommendation_type="goal_progress",
        title="Review your goal progress",
        message="Review the progress of your active goals.",
        source_signal="low_goal_progress",
        priority=0.7,
    )

    fetched = repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == test_user.id
    assert fetched.title == "Review your goal progress"

    db.close()


def test_get_recommendations_by_user(test_user):
    db = TestSessionLocal()

    repository = RecommendationRepository(db)

    first = repository.create(
        user_id=test_user.id,
        recommendation_type="task_management",
        title="First recommendation",
        message="First message",
        priority=0.5,
    )

    second = repository.create(
        user_id=test_user.id,
        recommendation_type="habit_management",
        title="Second recommendation",
        message="Second message",
        priority=0.8,
    )

    recommendations = repository.get_by_user(test_user.id)

    assert len(recommendations) == 2
    assert {recommendation.id for recommendation in recommendations} == {
        first.id,
        second.id,
    }

    db.close()


def test_get_active_recommendation_by_signal(test_user):
    db = TestSessionLocal()

    repository = RecommendationRepository(db)

    created = repository.create(
        user_id=test_user.id,
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        source_signal="task_pressure",
        priority=0.9,
    )

    fetched = repository.get_active_by_signal(
        test_user.id,
        "task_pressure",
    )

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == test_user.id
    assert fetched.source_signal == "task_pressure"
    assert fetched.status == "generated"

    db.close()



def test_update_recommendation_status_to_accepted(test_user):
    db = TestSessionLocal()
    repository = RecommendationRepository(db)

    recommendation = repository.create(
        user_id=test_user.id,
        recommendation_type="task_management",
        title="Reduce your pending task load",
        message="Review your pending tasks.",
        source_signal="task_pressure",
        priority=0.9,
    )

    updated = repository.update_status(
        recommendation.id,
        "accepted",
    )

    assert updated is not None
    assert updated.id == recommendation.id
    assert updated.status == "accepted"

    fetched = repository.get_by_id(recommendation.id)

    assert fetched is not None
    assert fetched.status == "accepted"

    db.close()


def test_update_recommendation_status_to_dismissed(test_user):
    db = TestSessionLocal()
    repository = RecommendationRepository(db)

    recommendation = repository.create(
        user_id=test_user.id,
        recommendation_type="goal_management",
        title="Review your goal progress",
        message="Choose one active goal and define a small next action.",
        source_signal="low_goal_progress",
        priority=0.7,
    )

    updated = repository.update_status(
        recommendation.id,
        "dismissed",
    )

    assert updated is not None
    assert updated.id == recommendation.id
    assert updated.status == "dismissed"

    fetched = repository.get_by_id(recommendation.id)

    assert fetched is not None
    assert fetched.status == "dismissed"

    db.close()


def test_update_recommendation_status_for_missing_recommendation(test_user):
    db = TestSessionLocal()
    repository = RecommendationRepository(db)

    missing_id = uuid.uuid4()

    updated = repository.update_status(
        missing_id,
        "accepted",
    )

    assert updated is None

    db.close()