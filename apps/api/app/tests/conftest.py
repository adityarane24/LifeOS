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

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from fastapi.testclient import TestClient

from main import app

from app.db.session import get_db

from app.models.user import User
from app.models.task import Task
from app.models.goal import Goal
from app.models.habit import Habit, HabitCompletion
from app.models.project import Project
from app.models.activity_event import ActivityEvent

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

    # Create a new test database session.
    db = TestSessionLocal()

    try:
        # Give the session to the API endpoint.
        yield db

    finally:
        # Always close the session after the request.
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

    # Create the FastAPI test client.
    test_client = TestClient(app)

    # Give the test access to the client.
    yield test_client

    # Create a database session connected to lifeos_test.
    db = TestSessionLocal()

    try:

        # Habit completions depend on habits.
        # Therefore they must be deleted first.
        db.query(HabitCompletion).delete()
        db.query(Habit).delete()
        db.query(Goal).delete()
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(ActivityEvent).delete()
        db.query(User).delete()
        db.commit()

    finally:
        # Always close the database session.
        db.close()


# ---------------------------------------------------------
# TEST USER FIXTURE
# ---------------------------------------------------------
#
# Some tests need a real user before they can create
# tasks, goals, or habits.
#
# We create the user directly in the TEST database.
#
# IMPORTANT:
# We return the SQLAlchemy User object rather than
# response.json().
#
# This allows tests to use:
#
#     test_user.id
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
        email="habit_test_runner@example.com",
        name="Habit Tester",
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

    finally:
        # Delete habit completions first.
        db.query(HabitCompletion).filter(
            HabitCompletion.habit_id.in_(
                db.query(Habit.id).filter(
                    Habit.user_id == user.id
                )
            )
        ).delete(synchronize_session=False)

        # Delete habits created by this test user.
        db.query(Habit).filter(
            Habit.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete activity events created by this test user.
        db.query(ActivityEvent).filter(
            ActivityEvent.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete goals created by this test user.
        db.query(Goal).filter(
            Goal.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete tasks created by this test user.
        db.query(Task).filter(
            Task.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete projects created by this test user.
        db.query(Project).filter(
            Project.user_id == user.id
        ).delete(synchronize_session=False)

        # Delete the user last because all dependent records
        # have now been removed.
        db.query(User).filter(
            User.id == user.id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()