from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "TwinFi AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-must-be-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Databases (with local dev defaults so app starts without full .env)
    DATABASE_URL: str = "sqlite+aiosqlite:///./twinfi.db"
    MONGO_URI: Optional[str] = None
    MONGO_DB_NAME: str = "twinfi_ai_docs"
    REDIS_URL: Optional[str] = None

    # ── Groq AI (replaces Azure OpenAI for local dev) ──────────────────────────
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-70b-8192"  # fast, free-tier friendly

    # Azure OpenAI (optional – production only)
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-large"

    # Azure AI Search (optional)
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_KEY: Optional[str] = None
    AZURE_SEARCH_INDEX: str = "twinfi-knowledge-base"

    # Kafka (optional – streaming features)
    KAFKA_BROKER_URL: str = "localhost:9092"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
