from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.llm import LLMError, complete
from app.schemas import AskRequest, AskResponse, ModelUsage, UsageResponse

app = FastAPI(title="Examate RAG starter", version="0.1.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]

_usage: dict = {"fallback_calls": 0, "by_model": {}}


def _track(result) -> None:
    model = result.model
    if model not in _usage["by_model"]:
        _usage["by_model"][model] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    entry = _usage["by_model"][model]
    entry["calls"] += 1
    entry["input_tokens"] += result.input_tokens
    entry["output_tokens"] += result.output_tokens
    entry["cost_usd"] += result.cost_usd
    if result.fallback_used:
        _usage["fallback_calls"] += 1


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Liveness: the process is up. Must be fast and must not call the LLM or the DB."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.post("/ask")
def ask(body: AskRequest) -> AskResponse:
    try:
        result = complete(body.question)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    _track(result)
    return AskResponse(answer=result.text, model=result.model, fallback_used=result.fallback_used)


@app.get("/usage")
def usage() -> UsageResponse:
    by_model = [
        ModelUsage(model=model, **data)
        for model, data in _usage["by_model"].items()
    ]
    return UsageResponse(
        total_calls=sum(m.calls for m in by_model),
        total_input_tokens=sum(m.input_tokens for m in by_model),
        total_output_tokens=sum(m.output_tokens for m in by_model),
        total_cost_usd=sum(m.cost_usd for m in by_model),
        fallback_calls=_usage["fallback_calls"],
        by_model=by_model,
    )
