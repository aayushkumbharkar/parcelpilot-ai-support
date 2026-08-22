from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    mock_mode: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
    snapshot_time: str = os.getenv("SNAPSHOT_TIME", "2026-08-21T12:00:00+05:30")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,https://parcelpilot-ai-support-two.vercel.app").split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()
