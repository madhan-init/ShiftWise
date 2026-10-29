from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    model: str
    fallback_used: bool


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
