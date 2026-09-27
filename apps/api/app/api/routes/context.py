from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.context import ContextResponse
from app.services.context import ContextService


router = APIRouter(
    prefix="/context",
    tags=["context"],
)


@router.get("", response_model=ContextResponse)
def get_user_context(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    context_service = ContextService(db)

    return context_service.get_user_context(user_id)