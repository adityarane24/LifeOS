from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """
    Contains business logic for projects.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProjectRepository(db)

    def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project.
        """

        project = Project(
            **data.model_dump()
        )

        self.repository.create(project)

        self.db.commit()
        self.db.refresh(project)

        return project

    def get_project(self, project_id: UUID) -> Project | None:
        """
        Get a project by its ID.
        """

        return self.repository.get_by_id(project_id)

    def get_user_projects(self, user_id: UUID) -> list[Project]:
        """
        Get all projects belonging to a user.
        """

        return self.repository.get_by_user(user_id)

    def update_project(
        self,
        project_id: UUID,
        data: ProjectUpdate,
    ) -> Project | None:
        """
        Update an existing project.
        """

        project = self.repository.get_by_id(project_id)

        if project is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(project, field, value)

        self.repository.update(project)

        self.db.commit()
        self.db.refresh(project)

        return project

    def delete_project(self, project_id: UUID) -> bool:
        """
        Delete a project.
        """

        project = self.repository.get_by_id(project_id)

        if project is None:
            return False

        self.repository.delete(project)

        self.db.commit()

        return True
    