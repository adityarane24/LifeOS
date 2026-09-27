from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.intelligence import IntelligenceResponse
from app.services.intelligence import IntelligenceService


router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
)


@router.get("", response_model=IntelligenceResponse)
def get_intelligence(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    intelligence_service = IntelligenceService(db)

    return intelligence_service.generate(user_id)