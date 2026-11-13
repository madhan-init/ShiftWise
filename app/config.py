from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "examate-rag"
    environment: str = "local"  # local | ci | production

    # LLM provider ("gemini" | "ollama")
    llm_provider: str = "gemini"
    llm_timeout_seconds: int = 60

    # Gemini settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_fallback_model: str = "gemini-1.5-flash-8b"
    gemini_input_price_per_million: float = 0.075
    gemini_output_price_per_million: float = 0.30

    # Ollama settings (fallback / alternative local provider & embeddings)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_fallback_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"
    embed_dimensions: int = 768
    chunk_page_lines: int = 50
    ollama_input_price_per_million: float = 0.0
    ollama_output_price_per_million: float = 0.0

    # Usage DB
    usage_db_path: str = "./usage.db"

    # Database (Postgres + pgvector)
    database_url: str = "postgresql://shiftwise:shiftwise@localhost:5432/shiftwise"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "shiftwise"
    postgres_password: str = "shiftwise"
    postgres_db: str = "shiftwise"


@lru_cache
def get_settings() -> Settings:
    return Settings()
