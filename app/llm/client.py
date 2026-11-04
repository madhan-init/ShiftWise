from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.config import Settings, get_settings


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    fallback_used: bool


class LLMError(RuntimeError):
    pass


class _RetryableError(Exception):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> LLMResult: ...


class OllamaProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._primary = settings.ollama_model
        self._fallback = settings.ollama_fallback_model
        self._timeout = settings.llm_timeout_seconds
        self._input_price = settings.ollama_input_price_per_million
        self._output_price = settings.ollama_output_price_per_million

    def complete(self, prompt: str) -> LLMResult:
        try:
            return self._call(self._primary, prompt, fallback_used=False)
        except _RetryableError:
            try:
                return self._call(self._fallback, prompt, fallback_used=True)
            except _RetryableError as exc:
                raise LLMError(
                    f"Both primary ('{self._primary}') and fallback ('{self._fallback}') "
                    f"models failed. Last error: {exc}"
                ) from exc

    def _call(self, model: str, prompt: str, *, fallback_used: bool) -> LLMResult:
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

        start = time.perf_counter()
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=payload)
        except httpx.ConnectError as exc:
            raise _RetryableError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Is Ollama running? Start it with 'ollama serve'."
            ) from exc
        except httpx.TimeoutException as exc:
            raise _RetryableError(f"Request to model '{model}' timed out after {self._timeout}s.") from exc
        latency_ms = (time.perf_counter() - start) * 1000

        if response.status_code >= 500:
            raise _RetryableError(f"Ollama returned HTTP {response.status_code} for model '{model}'.")

        response.raise_for_status()

        data = response.json()
        text = data["message"]["content"]
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)
        cost_usd = (
            input_tokens * self._input_price / 1_000_000 + output_tokens * self._output_price / 1_000_000
        )

        return LLMResult(
            text=text,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=round(latency_ms, 2),
            fallback_used=fallback_used,
        )


_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
}


def get_llm(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    provider_name = settings.llm_provider.lower()
    if provider_name not in _PROVIDERS:
        raise LLMError(
            f"Unknown LLM_PROVIDER '{provider_name}'. " f"Supported: {', '.join(sorted(_PROVIDERS))}"
        )
    return _PROVIDERS[provider_name](settings)


def complete(prompt: str, *, settings: Settings | None = None) -> LLMResult:
    return get_llm(settings).complete(prompt)
