from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.schemas.ai import AIResponse


class IntelligenceResponse(BaseModel):
    generated_at: datetime
    user_id: UUID
    context: dict[str, Any]
    signals: list[dict[str, Any]]
    prioritized_signals: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    ai_response: AIResponse