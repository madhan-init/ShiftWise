from unittest.mock import patch

import pytest

from app.llm import LLMError, LLMResult
from app.main import _usage


@pytest.fixture(autouse=True)
def _reset_usage():
    _usage["fallback_calls"] = 0
    _usage["by_model"].clear()
    yield
    _usage["fallback_calls"] = 0
    _usage["by_model"].clear()


def _fake_result(text="answer", model="llama3.1:8b", fallback_used=False):
    return LLMResult(
        text=text, model=model, input_tokens=10, output_tokens=5,
        cost_usd=0.0, latency_ms=100.0, fallback_used=fallback_used,
    )


class TestAsk:
    def test_success(self, client):
        with patch("app.main.complete", return_value=_fake_result(text="Hello!")):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 200
        data = r.json()
        assert data["answer"] == "Hello!"
        assert data["model"] == "llama3.1:8b"
        assert data["fallback_used"] is False

    def test_llm_error_returns_502(self, client):
        with patch("app.main.complete", side_effect=LLMError("Ollama is down")):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 502
        assert "Ollama is down" in r.json()["detail"]

    def test_missing_question_returns_422(self, client):
        r = client.post("/ask", json={})
        assert r.status_code == 422


class TestUsage:
    def test_empty_usage(self, client):
        r = client.get("/usage")
        assert r.status_code == 200
        data = r.json()
        assert data["total_calls"] == 0
        assert data["by_model"] == []

    def test_usage_after_calls(self, client):
        with patch("app.main.complete", return_value=_fake_result()):
            client.post("/ask", json={"question": "q1"})
            client.post("/ask", json={"question": "q2"})
        r = client.get("/usage")
        data = r.json()
        assert data["total_calls"] == 2
        assert data["total_input_tokens"] == 20
        assert data["total_output_tokens"] == 10
        assert data["fallback_calls"] == 0
        assert len(data["by_model"]) == 1

    def test_fallback_tracked(self, client):
        with patch("app.main.complete", return_value=_fake_result(fallback_used=True)):
            client.post("/ask", json={"question": "q"})
        r = client.get("/usage")
        assert r.json()["fallback_calls"] == 1

