from typing import Any

from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    provider: str
    response: str
    source_signal: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)