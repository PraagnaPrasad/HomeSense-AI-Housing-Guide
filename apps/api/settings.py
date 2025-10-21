import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "local"
    pplx_api_key: str | None = None
    fred_api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

settings = Settings()

# Also set environment variables for compatibility with code that uses os.environ
if settings.pplx_api_key:
    os.environ["PPLX_API_KEY"] = settings.pplx_api_key
if settings.fred_api_key:
    os.environ["FRED_API_KEY"] = settings.fred_api_key