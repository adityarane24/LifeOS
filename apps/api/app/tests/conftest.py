# ---------------------------------------------------------
# PYTEST CONFIGURATION
# ---------------------------------------------------------
#
# This file contains reusable setup for our tests.
#
# Tests use:
#
#     lifeos_test
#
# instead of the development database:
#
#     lifeos
# ---------------------------------------------------------


# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

import uuid

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from main import app

from app.db.session import get_db

from app.models.user import User
from app.models.task import Task
from app.models.goal import Goal
from app.models.habit import Habit, HabitCompletion
from app.models.project import Project
from app.models.activity_event import ActivityEvent
from app.models.recommendation import Recommendation


# ---------------------------------------------------------
# TEST DATABASE URL
# ---------------------------------------------------------
#
# This database is completely separate from our
# development database.
# ---------------------------------------------------------

TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    "lifeos:lifeos_dev_password@"
    "localhost:5432/lifeos_test"
)


# ---------------------------------------------------------
# TEST DATABASE ENGINE
# ---------------------------------------------------------

test_engine = create_engine(
    TEST_DATABASE_URL,

    # Keep SQL logging enabled while we are learning
    # and debugging the test setup.
    echo=True,
)


# ---------------------------------------------------------
# TEST SESSION FACTORY
# ---------------------------------------------------------

TestSessionLocal = sessionmaker(
    bind=test_engine,

    # We explicitly control commits in our application.
    autocommit=False,

    # Keep objects usable after commit.
    expire_on_commit=False,
)


# ---------------------------------------------------------
# TEST DATABASE DEPENDENCY
# ---------------------------------------------------------
#
# This function works like our normal get_db().
#
# The difference is that it creates sessions using
# test_engine instead of the development engine.
# ---------------------------------------------------------

def override_get_db():
    """
    Provide a database session connected to lifeos_test.
    """

    db = TestSessionLocal()

    try:
        yield db

    finally:
        db.close()


# ---------------------------------------------------------
# FASTAPI DEPENDENCY OVERRIDE
# ---------------------------------------------------------
#
# During tests, whenever FastAPI asks for:
#
#     get_db
#
# it will use:
#
#     override_get_db
#
# This makes sure our API tests never use the
# development database.
# ---------------------------------------------------------

app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------
# TEST CLIENT FIXTURE
# ---------------------------------------------------------

@pytest.fixture
def client():
    """
    Create a FastAPI test client.

    The test database is cleaned after each test so
    every test starts with an empty database.
    """

    test_client = TestClient(app)

    yield test_client

    db = TestSessionLocal()

    try:
        # Recommendations depend on users.
        # Therefore they must be deleted first.
        db.query(Recommendation).delete()

        # Habit completions depend on habits.
        db.query(HabitCompletion).delete()

        db.query(Habit).delete()
        db.query(Goal).delete()
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(ActivityEvent).delete()

        # Users are deleted last because all dependent
        # records have now been removed.
        db.query(User).delete()

        db.commit()

    finally:
        db.close()


# ---------------------------------------------------------
# TEST USER FIXTURE
# ---------------------------------------------------------
#
# Some tests need a real user before they can create
# tasks, goals, habits, projects, etc.
#
# A unique email is generated for every test run.
# This prevents duplicate-email errors when tests are
# executed repeatedly.
# ---------------------------------------------------------

@pytest.fixture
def test_user():
    """
    Create a temporary user in the test database
    and clean up everything belonging to that user
    after the test finishes.
    """

    db = TestSessionLocal()

    user = User(
        email=f"habit_test_runner_{uuid.uuid4().hex}@example.com",
        name="Habit Tester",
    )

    try:
        # Create the test user.
        db.add(user)
        db.commit()
        db.refresh(user)

        # Give the test access to the SQLAlchemy User object.
        yield user

    finally:
        # Only perform user-specific cleanup if the user
        # was successfully created.
        if user.id is not None:

            # Recommendations reference users,
            # so delete them first.
            db.query(Recommendation).filter(
                Recommendation.user_id == user.id
            ).delete(synchronize_session=False)

            # Habit completions reference habits,
            # so delete them before habits.
            db.query(HabitCompletion).filter(
                HabitCompletion.habit_id.in_(
                    db.query(Habit.id).filter(
                        Habit.user_id == user.id
                    )
                )
            ).delete(synchronize_session=False)

            # Delete habits.
            db.query(Habit).filter(
                Habit.user_id == user.id
            ).delete(synchronize_session=False)

            # Delete activity events.
            db.query(ActivityEvent).filter(
                ActivityEvent.user_id == user.id
            ).delete(synchronize_session=False)

            # Delete goals.
            db.query(Goal).filter(
                Goal.user_id == user.id
            ).delete(synchronize_session=False)

            # Delete tasks.
            db.query(Task).filter(
                Task.user_id == user.id
            ).delete(synchronize_session=False)

            # Delete projects.
            db.query(Project).filter(
                Project.user_id == user.id
            ).delete(synchronize_session=False)

            # Delete the user last.
            db.query(User).filter(
                User.id == user.id
            ).delete(synchronize_session=False)

            db.commit()

        # Always close the database session.
        db.close()