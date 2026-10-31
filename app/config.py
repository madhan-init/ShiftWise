from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "examate-rag"
    environment: str = "local"  # local | ci | production

    # LLM provider
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_fallback_model: str = "llama3.1:8b"
    llm_timeout_seconds: int = 60

    # Cost per million tokens (0 for local models)
    ollama_input_price_per_million: float = 0.0
    ollama_output_price_per_million: float = 0.0

    # Usage DB
    usage_db_path: str = "./usage.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
