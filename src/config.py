from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env explicitly with absolute path
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)
print(f"📁 Loading .env from: {env_path}")

class Settings(BaseSettings):
    APP_NAME: str = "Autonomous Issue Resolver"
    DEBUG: bool = False
    
    # GitHub
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_TOKEN: str = ""
    
    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    LLM_MODEL: str = ""
    
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra env vars that aren't defined
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Debug print
print(f"🔑 API Key loaded: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
print(f"🔗 Base URL: {settings.OPENAI_BASE_URL}")
print(f"🤖 Model: {settings.LLM_MODEL}")