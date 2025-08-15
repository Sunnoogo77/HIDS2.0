# backend/app/core/config.py
import logging
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    APP_NAME: str       = "HIDS-Web API"
    VERSION: str        = "2.0.0"
    API_V1_STR: str     = "/api"
    DATABASE_URL: str   = Field("sqlite:///./data/hids.db", env="DATABASE_URL")
    LOG_LEVEL: str      = Field("INFO", env="LOG_LEVEL")
    JWT_SECRET: str     = Field(..., env="JWT_SECRET")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
