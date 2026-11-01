"""Tests for app.llm — LLM client with Ollama provider."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from app.config import Settings
from app.llm import LLMError, LLMResult, OllamaProvider, complete, get_llm


def _settings(**overrides) -> Settings:
    """Build a Settings instance with sensible test defaults."""
    defaults: dict = {
        "app_name": "examate-rag",
        "environment": "test",
        "llm_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model": "llama3.1:8b",
        "ollama_fallback_model": "llama3.1:8b",
        "llm_timeout_seconds": 5,
        "ollama_input_price_per_million": 0.0,
        "ollama_output_price_per_million": 0.0,
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _ollama_json(content: str = "Hello!", prompt_eval_count: int = 10, eval_count: int = 5) -> dict:
    """Build a realistic Ollama /api/chat JSON body."""
    return {
        "message": {"role": "assistant", "content": content},
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
    }


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
    """Build a mock httpx.Response."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or _ollama_json()
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"HTTP {status_code}", request=MagicMock(), response=resp
        )
    return resp


@pytest.fixture
def mock_httpx(monkeypatch):
    """Patch httpx.Client so tests never hit the network."""
    responses: list = []

    class _MockClient:
        def __init__(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

        def post(self, _url, **_kwargs):
            if not responses:
                raise RuntimeError("No mock responses left")
            action = responses.pop(0)
            if isinstance(action, Exception):
                raise action
            return action

    monkeypatch.setattr("app.llm.httpx.Client", _MockClient)
    return responses


class TestOllamaSuccess:
    def test_returns_llm_result(self, mock_httpx):
        mock_httpx.append(_mock_response(json_data=_ollama_json("Hi!", 20, 12)))

        result = complete("Say hi", settings=_settings())

        assert isinstance(result, LLMResult)
        assert result.text == "Hi!"
        assert result.model == "llama3.1:8b"
        assert result.input_tokens == 20
        assert result.output_tokens == 12
        assert result.cost_usd == 0.0
        assert result.fallback_used is False
        assert result.latency_ms >= 0

    def test_cost_calculation_with_nonzero_prices(self, mock_httpx):
        mock_httpx.append(_mock_response(json_data=_ollama_json("x", 1_000, 500)))

        settings = _settings(
            ollama_input_price_per_million=3.0,
            ollama_output_price_per_million=15.0,
        )
        result = complete("x", settings=settings)

        expected = 1_000 * 3.0 / 1_000_000 + 500 * 15.0 / 1_000_000
        assert result.cost_usd == pytest.approx(expected)

    def test_missing_token_counts_default_to_zero(self, mock_httpx):
        json_data = {"message": {"role": "assistant", "content": "ok"}}
        mock_httpx.append(_mock_response(json_data=json_data))

        result = complete("hi", settings=_settings())

        assert result.input_tokens == 0
        assert result.output_tokens == 0


class TestOllamaFallback:
    def test_timeout_triggers_fallback(self, mock_httpx):
        mock_httpx.append(httpx.ReadTimeout("timed out"))
        mock_httpx.append(_mock_response(json_data=_ollama_json("fallback answer")))

        result = complete("hi", settings=_settings())

        assert result.fallback_used is True
        assert result.text == "fallback answer"

    def test_connect_error_triggers_fallback(self, mock_httpx):
        mock_httpx.append(httpx.ConnectError("refused"))
        mock_httpx.append(_mock_response(json_data=_ollama_json("ok")))

        result = complete("hi", settings=_settings())

        assert result.fallback_used is True
        assert result.text == "ok"

    def test_5xx_triggers_fallback(self, mock_httpx):
        mock_httpx.append(_mock_response(status_code=503))
        mock_httpx.append(_mock_response(json_data=_ollama_json("recovered")))

        result = complete("hi", settings=_settings())

        assert result.fallback_used is True
        assert result.text == "recovered"


class TestOllamaBothFail:
    def test_both_timeout_raises_llm_error(self, mock_httpx):
        mock_httpx.append(httpx.ReadTimeout("primary timeout"))
        mock_httpx.append(httpx.ReadTimeout("fallback timeout"))

        with pytest.raises(LLMError, match="Both primary"):
            complete("hi", settings=_settings())

    def test_connection_refused_says_ollama_not_running(self, mock_httpx):
        mock_httpx.append(httpx.ConnectError("refused"))
        mock_httpx.append(httpx.ConnectError("refused"))

        with pytest.raises(LLMError, match="Is Ollama running"):
            complete("hi", settings=_settings())

    def test_both_5xx_raises_llm_error(self, mock_httpx):
        mock_httpx.append(_mock_response(status_code=500))
        mock_httpx.append(_mock_response(status_code=502))

        with pytest.raises(LLMError, match="Both primary"):
            complete("hi", settings=_settings())


class TestProviderFactory:
    def test_default_provider_is_ollama(self):
        llm = get_llm(_settings())
        assert isinstance(llm, OllamaProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(LLMError, match="Unknown LLM_PROVIDER"):
            get_llm(_settings(llm_provider="openai"))
