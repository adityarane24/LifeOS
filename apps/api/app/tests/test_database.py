# ---------------------------------------------------------
# DATABASE TESTS
# ---------------------------------------------------------
#
# These tests verify that our test database is reachable
# and that SQLAlchemy can communicate with PostgreSQL.
# ---------------------------------------------------------


from sqlalchemy import text

from app.tests.conftest import TestSessionLocal


def test_database_session():
    """
    Test that a SQLAlchemy session can communicate
    with the test PostgreSQL database.
    """

    # Create a database session connected to lifeos_test.
    db = TestSessionLocal()

    try:
        # Execute a harmless SQL query.
        result = db.execute(text("SELECT 1"))

        # Get the value returned by PostgreSQL.
        value = result.scalar()

        # Verify that PostgreSQL returned the expected value.
        assert value == 1

    finally:
        # Always close the database session.
        db.close()