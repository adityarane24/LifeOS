from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ContextSignal(BaseModel):
    type: str
    severity: str
    message: str
    source: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)


class ContextAnalysis(BaseModel):
    analyzed_at: datetime
    signal_count: int
    signals: list[ContextSignal]