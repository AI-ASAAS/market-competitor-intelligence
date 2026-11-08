import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "مهندس تحليل الأعمال والمنافسين | ASAAS Market Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = int(os.environ.get("PORT", "8008"))
    HOST: str = "127.0.0.1"
    
    # API Keys (Loaded from .env or environment)
    TAVILY_API_KEY: Optional[str] = os.environ.get("TAVILY_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.environ.get("OPENROUTER_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")
    
    # Model preferences
    DEFAULT_LLM_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
    SUPPORTED_MODELS: list = [
        {"id": "nvidia/nemotron-3.5-lightning:free", "name": "Nvidia Nemotron 3.5 (مجاني فائق الذكاء - موصى به)"},
        {"id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash (سريع ودقيق)"},
        {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet (الأعلى احترافية في التحليل)"},
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini (سريع واقتصادي)"},
        {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3 (قوي في اللغة والتحليل)"},
        {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B (مفتوح ومتقدم)"}
    ]
    
    # Database
    DATABASE_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "market_intelligence.db")
    
    # Regional defaults
    DEFAULT_REGION: str = "السوق العربي"
    
    # HTTP Scraper Settings
    SCRAPER_TIMEOUT_SECONDS: float = 15.0
    SCRAPER_MAX_CHARS: int = 15000
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 "
        "(ASAAS Competitor Intelligence Bot/1.0)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
