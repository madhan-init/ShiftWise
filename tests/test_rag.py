from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.llm import LLMResult
from app.rag import (
    build_rag_prompt,
    extract_citations,
    format_citation,
    normalize_version,
    query_rag,
)


def _sample_chunks():
    return [
        {
            "id": 1,
            "version": "3.3",
            "document": "org/springframework/boot/autoconfigure/data/redis/RedisProperties.java",
            "page": 2,
            "heading": "class RedisProperties",
            "start_line": 51,
            "end_line": 100,
            "content": "private String host = \"localhost\";\nprivate int port = 6379;",
            "score": 0.89,
            "metadata": {},
        },
        {
            "id": 2,
            "version": "3.3",
            "document": "org/springframework/boot/autoconfigure/web/ServerProperties.java",
            "page": 4,
            "heading": "class ServerProperties",
            "start_line": 151,
            "end_line": 200,
            "content": "private Duration timeout = Duration.ofMinutes(30);",
            "score": 0.82,
            "metadata": {},
        },
    ]


def test_normalize_version():
    assert normalize_version("3.3.13") == "3.3"
    assert normalize_version("2.7.18") == "2.7"
    assert normalize_version("3.5") == "3.5"
    assert normalize_version(None) is None


def test_format_citation():
    assert (
        format_citation("org/springframework/boot/autoconfigure/data/redis/RedisProperties.java", 2)
        == "[RedisProperties.java, Page 2]"
    )


def test_extract_citations():
    text = "The property was moved in [RedisProperties.java, Page 2] and also configured in [ServerProperties.java, Page 4]."
    citations = extract_citations(text)
    assert citations == ["[RedisProperties.java, Page 2]", "[ServerProperties.java, Page 4]"]


def test_build_rag_prompt():
    chunks = _sample_chunks()
    prompt = build_rag_prompt("What is the host property?", chunks, version="3.3")

    assert "[RedisProperties.java, Page 2]" in prompt
    assert "Version: 3.3" in prompt
    assert "Target version requested: 3.3" in prompt
    assert "What is the host property?" in prompt
    assert "STRICT VERSION ISOLATION" in prompt


def test_query_rag_with_vector_search_and_citations():
    fake_chunks = _sample_chunks()
    fake_llm_result = LLMResult(
        text="In Spring Boot 3.3, redis properties are defined in [RedisProperties.java, Page 2].",
        model="gemini-1.5-flash",
        input_tokens=150,
        output_tokens=30,
        cost_usd=0.00002,
        latency_ms=250.0,
        fallback_used=False,
    )

    mock_embedder = MagicMock()
    mock_embedder.embed_text.return_value = [0.1] * 768

    with patch("app.rag.get_embedder", return_value=mock_embedder), \
         patch("app.rag.search_chunks", return_value=fake_chunks), \
         patch("app.rag.complete", return_value=fake_llm_result):
        result, citations = query_rag(
            question="Where is redis host defined?",
            version="3.3",
            top_k=2,
        )

    assert result.text == fake_llm_result.text
    assert citations == ["[RedisProperties.java, Page 2]"]
    mock_embedder.embed_text.assert_called_once_with("Where is redis host defined?")


def test_query_rag_filters_hallucinated_citations():
    fake_chunks = _sample_chunks()
    fake_llm_result = LLMResult(
        text="The property is in [FakeClass.java, Page 99] and [RedisProperties.java, Page 2].",
        model="gemini-1.5-flash",
        input_tokens=100,
        output_tokens=20,
        cost_usd=0.00001,
        latency_ms=200.0,
        fallback_used=False,
    )

    with patch("app.rag.get_embedder"), \
         patch("app.rag.search_chunks", return_value=fake_chunks), \
         patch("app.rag.complete", return_value=fake_llm_result):
        _result, citations = query_rag(
            question="Where is it?",
            version="3.3",
        )

    # Only citations matching retrieved chunks are kept (FakeClass.java, Page 99 rejected)
    assert citations == ["[RedisProperties.java, Page 2]"]


def test_ask_endpoint_with_version_and_citations(client):
    fake_chunks = _sample_chunks()
    fake_llm_result = LLMResult(
        text="The host is defined in [RedisProperties.java, Page 2].",
        model="gemini-1.5-flash",
        input_tokens=120,
        output_tokens=25,
        cost_usd=0.000015,
        latency_ms=220.0,
        fallback_used=False,
    )

    with patch("app.rag.get_embedder"), \
         patch("app.rag.search_chunks", return_value=fake_chunks), \
         patch("app.main.complete", return_value=fake_llm_result):
        response = client.post(
            "/ask",
            json={"question": "What is redis host?", "version": "3.3"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == fake_llm_result.text
    assert data["version"] == "3.3"
    assert data["citations"] == ["[RedisProperties.java, Page 2]"]
    assert data["model"] == "gemini-1.5-flash"
    assert data["fallback_used"] is False
