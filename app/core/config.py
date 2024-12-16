from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    # API Keys
    ANTHROPIC_API_KEY: str
    BRAVE_API_KEY: str
    OPENAI_API_KEY: str
    
    # Output Configuration
    OUTPUT_DIR: str = "outputs"
    
    # Search Configuration
    MAX_SEARCH_RESULTS: int = 5
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
