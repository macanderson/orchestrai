import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "OrchestrAI"
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://docuchat.vercel.app",
    ]  # noqa: E501

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/orchestrai",  # noqa: E501
    )

    # Vector database settings
    VECTOR_DIMENSION: int = 384  # all-MiniLM-L6-v2 dimension

    # LLM settings
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o")
    LLM_TEMPERATURE: float = 0.0

    # Document processing
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Redis
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Supabase
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

    # Crawling settings
    MAX_URLS_PER_PROJECT: int = 100
    MAX_WORKERS: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
