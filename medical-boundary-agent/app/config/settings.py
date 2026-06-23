from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Medical Boundary Agent"
    DEBUG: bool = False

    # LLM
    DEEPSEEK_API_KEY: str = "sk-46b656d4ec5147589d400d18f656a088"
    DEEPSEEK_API_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 1024

    # Database
    DATABASE_URL: str = "sqlite:///./medical_agent.db"

    # Vector Store
    FAISS_INDEX_PATH: str = "app/vectorstore/faiss_index"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # RAG
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.5

    # Confidence
    CONFIDENCE_THRESHOLD: float = 0.6
    SEMANTIC_WEIGHT: float = 0.6
    COVERAGE_WEIGHT: float = 0.4

    # Memory
    MEMORY_MAX_TURNS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
