from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.schemas.context_signal import ContextAnalysis


class ContextResponse(BaseModel):
    generated_at: datetime
    user_id: UUID

    tasks: dict[str, Any]
    goals: dict[str, Any]
    habits: dict[str, Any]
    projects: dict[str, Any]
    recent_activity: dict[str, Any]
    analytics: dict[str, Any]
    analysis: ContextAnalysis