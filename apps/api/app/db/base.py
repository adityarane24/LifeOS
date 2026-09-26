# ---------------------------------------------------------
# SQLAlchemy Base
# ---------------------------------------------------------
#
# All of our database models will inherit from this Base.
#
# For example:
#
# class User(Base):
#     ...
#
# class Task(Base):
#     ...
#
# SQLAlchemy uses this Base to keep track of all the
# database models in our application.

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all LifeOS database models.

    Every SQLAlchemy model we create will inherit from
    this class.
    """

    pass