import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://duobites:duobites@localhost:5432/duobites",
)
APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

__all__ = ["BASE_DIR", "DATABASE_URL", "APP_ENV", "SECRET_KEY"]
