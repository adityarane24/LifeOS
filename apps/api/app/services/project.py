# ---------------------------------------------------------
# Project Service
# ---------------------------------------------------------
#
# This file contains the business logic related to projects.
#
# The service sits between the API routes and the
# repository layer.
#
# Route → Service → Repository → Database


from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)
from app.models.project import Project, ProjectStatus
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.activity_event import ActivityEventService


class ProjectService:
    """
    Contains business logic for projects.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProjectRepository(db)
        self.activity_event_service = ActivityEventService(db)

    # -----------------------------------------------------
    # CREATE PROJECT
    # -----------------------------------------------------

    def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project.
        """

        project = Project(
            **data.model_dump()
        )

        self.repository.create(project)

        # Create an activity event for the new project.
        self.activity_event_service.create_event(
            user_id=project.user_id,
            event_type=ActivityEventType.project_created,
            entity_type=ActivityEntityType.project,
            entity_id=project.id,
            event_metadata={
                "title": project.title,
                "priority": project.priority.value,
            },
        )

        # Commit both the project and its activity event
        # in the same database transaction.
        self.db.commit()

        self.db.refresh(project)

        return project

    # -----------------------------------------------------
    # GET PROJECT
    # -----------------------------------------------------

    def get_project(self, project_id: UUID) -> Project | None:
        """
        Get a project by its ID.
        """

        return self.repository.get_by_id(project_id)

    # -----------------------------------------------------
    # GET USER PROJECTS
    # -----------------------------------------------------

    def get_user_projects(
        self,
        user_id: UUID,
    ) -> list[Project]:
        """
        Get all projects belonging to a user.
        """

        return self.repository.get_by_user(user_id)

    # -----------------------------------------------------
    # UPDATE PROJECT
    # -----------------------------------------------------

    def update_project(
        self,
        project_id: UUID,
        data: ProjectUpdate,
    ) -> Project | None:
        """
        Update an existing project.

        Normal changes create project_updated.

        Changing the status to completed creates
        project_completed.

        Changing the status to archived creates
        project_archived.
        """

        # Find the project first.
        project = self.repository.get_by_id(project_id)

        if project is None:
            return None

        # Save the old status before applying updates.
        old_status = project.status

        # Get only fields supplied by the client.
        update_data = data.model_dump(
            exclude_unset=True
        )

        # Apply the supplied changes.
        for field, value in update_data.items():
            setattr(project, field, value)

        self.repository.update(project)

        # By default, this is a normal project update.
        event_type = ActivityEventType.project_updated

        # Check for important lifecycle transitions.
        if "status" in update_data:

            new_status = project.status

            # Project was completed.
            if new_status == ProjectStatus.completed:
                event_type = ActivityEventType.project_completed

            # Project was archived.
            elif new_status == ProjectStatus.archived:
                event_type = ActivityEventType.project_archived

        # Create the activity event.
        self.activity_event_service.create_event(
            user_id=project.user_id,
            event_type=event_type,
            entity_type=ActivityEntityType.project,
            entity_id=project.id,
            event_metadata={
                "updated_fields": list(update_data.keys()),
                "old_status": old_status.value,
                "new_status": project.status.value,
            },
        )

        # Commit both the project update and the
        # activity event in the same transaction.
        self.db.commit()

        self.db.refresh(project)

        return project

    # -----------------------------------------------------
    # DELETE PROJECT
    # -----------------------------------------------------

    def delete_project(self, project_id: UUID) -> bool:
        """
        Delete a project.

        Returns:
            True if the project was deleted.
            False if the project did not exist.
        """

        project = self.repository.get_by_id(project_id)

        if project is None:
            return False

        self.repository.delete(project)

        self.db.commit()

        return True