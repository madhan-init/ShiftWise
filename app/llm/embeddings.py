from __future__ import annotations

import httpx

from app.config import Settings, get_settings


class EmbeddingError(RuntimeError):
    pass


class OllamaEmbedder:
    """Generates vector embeddings using Ollama (nomic-embed-text)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._base_url = self._settings.ollama_base_url.rstrip("/")
        self._model = self._settings.ollama_embed_model
        self._timeout = self._settings.llm_timeout_seconds

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        url = f"{self._base_url}/api/embeddings"
        payload = {"model": self._model, "prompt": text}
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 404:
                    # Try newer /api/embed endpoint
                    resp = client.post(
                        f"{self._base_url}/api/embed",
                        json={"model": self._model, "input": text},
                    )
        except httpx.ConnectError as exc:
            raise EmbeddingError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Ensure Ollama is running and 'nomic-embed-text' model is pulled."
            ) from exc
        except httpx.TimeoutException as exc:
            raise EmbeddingError(f"Embedding request timed out after {self._timeout}s.") from exc

        if resp.status_code >= 400:
            raise EmbeddingError(f"Ollama embedding failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        if "embedding" in data:
            return data["embedding"]
        if "embeddings" in data and len(data["embeddings"]) > 0:
            return data["embeddings"][0]
        raise EmbeddingError(f"Unexpected response from Ollama: {data}")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""
        return [self.embed_text(t) for t in texts]


def get_embedder(settings: Settings | None = None) -> OllamaEmbedder:
    return OllamaEmbedder(settings)

