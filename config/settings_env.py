from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseSettings):
    """Конфигурация проекта через переменные окружения и Pydantic."""

    model_config = SettingsConfigDict(
        env_prefix="DJANGO_",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    secret_key: str = Field(..., description="SECRET_KEY Django.")
    debug: bool = Field(default=True, description="Режим DEBUG.")
    allowed_hosts_raw: str = Field(
        default="",
        alias="allowed_hosts",
        description="Список хостов через запятую или JSON.",
    )
    db_name: str = Field(
        default="db.sqlite3",
        description="Имя файла SQLite в корне проекта.",
    )

    @property
    def allowed_hosts(self) -> List[str]:
        raw = self.allowed_hosts_raw.strip()
        if not raw:
            return []
        return [host.strip() for host in raw.split(",") if host.strip()]


app_settings = AppSettings()

