from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.db import get_usage, init_db, log_call
from app.llm import LLMError, complete
from app.schemas import AskRequest, AskResponse, ModelUsage, UsageResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db(get_settings().usage_db_path)
    yield


app = FastAPI(title="Examate RAG starter", version="0.1.0", lifespan=lifespan)

SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Liveness: the process is up. Must be fast and must not call the LLM or the DB."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.post("/ask")
def ask(body: AskRequest, settings: SettingsDep) -> AskResponse:
    db = settings.usage_db_path
    try:
        result = complete(body.question)
    except LLMError as exc:
        log_call(
            db,
            model="unknown",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            fallback_used=False,
            latency_ms=0.0,
            status="error",
        )
        raise HTTPException(status_code=502, detail=str(exc))
    log_call(
        db,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=result.cost_usd,
        fallback_used=result.fallback_used,
        latency_ms=result.latency_ms,
    )
    return AskResponse(answer=result.text, model=result.model, fallback_used=result.fallback_used)


@app.get("/usage")
def usage(settings: SettingsDep) -> UsageResponse:
    data = get_usage(settings.usage_db_path)
    by_model = [ModelUsage(**entry) for entry in data["by_model"]]
    return UsageResponse(
        total_calls=data["total_calls"],
        total_input_tokens=data["total_input_tokens"],
        total_output_tokens=data["total_output_tokens"],
        total_cost_usd=data["total_cost_usd"],
        fallback_calls=data["fallback_calls"],
        by_model=by_model,
    )
