from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    """
    Handles database operations for projects.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: UUID) -> Project | None:
        """
        Find a project using its ID.
        """

        statement = select(Project).where(
            Project.id == project_id
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_by_user(self, user_id: UUID) -> list[Project]:
        """
        Get all projects belonging to a user.
        """

        statement = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def create(self, project: Project) -> Project:
        """
        Add a new project to the database.
        """

        self.db.add(project)
        self.db.flush()

        return project

    def update(self, project: Project) -> Project:
        """
        Save changes made to a project.
        """

        self.db.flush()

        return project

    def delete(self, project: Project) -> None:
        """
        Delete a project from the database.
        """

        self.db.delete(project)
        self.db.flush()