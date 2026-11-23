from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str
    version: str | None = Field(
        default=None, description="Target Spring Boot version filter (e.g. '2.7', '3.3', '3.5')"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks to retrieve")


class AskResponse(BaseModel):
    answer: str
    model: str
    fallback_used: bool
    version: str | None = None
    citations: list[str] = Field(
        default_factory=list, description="Verified citations referenced in answer [document, Page X]"
    )


class ModelUsage(BaseModel):
    model: str
    calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: float


class UsageResponse(BaseModel):
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    fallback_calls: int
    by_model: list[ModelUsage]
