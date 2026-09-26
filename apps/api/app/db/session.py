# ---------------------------------------------------------
# DATABASE SESSION
# ---------------------------------------------------------
#
# This file is responsible for:
#
# 1. Creating the SQLAlchemy engine.
# 2. Creating database sessions.
# 3. Providing a FastAPI dependency that safely gives each request a database session.
#
# Architecture:
#
# FastAPI
#    ↓
# get_db()
#    ↓
# Session
#    ↓
# SQLAlchemy Engine
#    ↓
# PostgreSQL


from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


# ---------------------------------------------------------
# DATABASE ENGINE
# ---------------------------------------------------------
#
# The engine is the main SQLAlchemy object responsible
# for communicating with PostgreSQL.
#
# It also manages a connection pool so database
# connections can be reused efficiently.

engine = create_engine(
    settings.database_url,

    # Print SQL statements while developing.
    #
    # This is useful for learning and debugging.
    # We will disable this in production.
    echo=True,
)


# ---------------------------------------------------------
# SESSION FACTORY
# ---------------------------------------------------------
#
# sessionmaker creates a factory that can produce new
# SQLAlchemy Session objects.
#
# Each call to SessionLocal() creates a new session.

SessionLocal = sessionmaker(
    bind=engine,

    # SQLAlchemy should NOT automatically commit
    # transactions for us.
    #
    # We will explicitly control commits.
    autocommit=False,

    # Prevent SQLAlchemy from automatically expiring
    # objects after commit.
    #
    # This makes it easier to use returned objects after
    # session.commit().
    expire_on_commit=False,
)


# ---------------------------------------------------------
# FASTAPI DATABASE DEPENDENCY
# ---------------------------------------------------------
#
# FastAPI will use this function to provide a database
# session to API endpoints.
#
# Example:
#
# @router.post("/users")
# def create_user(db: Session = Depends(get_db)):
#     ...
#
# The "yield" means:
#
#     Before yield → create session
#     After yield  → close session


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for one request.

    The session is always closed when the request
    finishes, even if an error occurs.
    """

    # Create a new database session.
    db = SessionLocal()

    try:
        # Give the session to the FastAPI endpoint.
        yield db

    finally:
        # Always close the session after the request.
        #
        # This prevents database resources from being
        # left open accidentally.
        db.close()