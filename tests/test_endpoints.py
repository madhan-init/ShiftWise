from unittest.mock import patch

from app.llm import LLMError, LLMResult


def _fake_result(text="answer", model="llama3.1:8b", fallback_used=False):
    return LLMResult(
        text=text,
        model=model,
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.0,
        latency_ms=100.0,
        fallback_used=fallback_used,
    )


class TestAskPrimarySucceeds:
    def test_returns_answer(self, client):
        with patch("app.main.complete", return_value=_fake_result(text="Hello!")):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 200
        data = r.json()
        assert data["answer"] == "Hello!"
        assert data["model"] == "llama3.1:8b"
        assert data["fallback_used"] is False


class TestAskFallback:
    def test_fallback_answers(self, client):
        with patch("app.main.complete", return_value=_fake_result(text="fallback", fallback_used=True)):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 200
        assert r.json()["fallback_used"] is True
        assert r.json()["answer"] == "fallback"


class TestAskBothFail:
    def test_returns_502(self, client):
        with patch("app.main.complete", side_effect=LLMError("Both models failed")):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 502
        assert "Both models failed" in r.json()["detail"]


class TestAskOllamaNotRunning:
    def test_clear_error_message(self, client):
        err = "Is Ollama running? Start it with 'ollama serve'."
        with patch("app.main.complete", side_effect=LLMError(err)):
            r = client.post("/ask", json={"question": "hi"})
        assert r.status_code == 502
        assert "Is Ollama running" in r.json()["detail"]


class TestAskValidation:
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

    def test_usage_totals_after_two_calls(self, client):
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
        assert data["by_model"][0]["calls"] == 2

    def test_fallback_call_tracked(self, client):
        with patch("app.main.complete", return_value=_fake_result(fallback_used=True)):
            client.post("/ask", json={"question": "q"})
        r = client.get("/usage")
        assert r.json()["fallback_calls"] == 1

    def test_failed_call_logged(self, client):
        with patch("app.main.complete", side_effect=LLMError("down")):
            client.post("/ask", json={"question": "q"})
        r = client.get("/usage")
        assert r.json()["total_calls"] == 1
