from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    # API Keys
    ANTHROPIC_API_KEY: str = ""  # Changed from CLAUDE_API_KEY to match Anthropic's expected env var
    BRAVE_API_KEY: str
    OPENAI_API_KEY: str
    
    # Agent Configuration
    MAX_SEARCH_RESULTS: int = 10
    DAYS_LOOKBACK: int = 1
    
    # Output Configuration
    OUTPUT_DIR: str = "outputs"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
