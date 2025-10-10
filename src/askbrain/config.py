from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from dotenv import dotenv_values
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


class Settings(BaseModel):
    origin_host: AnyHttpUrl = Field(alias="ORIGIN_HOST")
    tilda_feed_uids: tuple[str, ...] = Field(alias="TILDA_FEED_UIDS")
    tilda_default_size: int = Field(alias="TILDA_SIZE", default=100)
    tilda_concurrency: int = Field(alias="TILDA_CONCURRENCY", default=2)

    @field_validator("tilda_feed_uids", mode="before")
    @classmethod
    def split_uids(cls, value: str | Iterable[str]) -> tuple[str, ...]:
        if isinstance(value, str):
            items = [item.strip() for item in value.split(",") if item.strip()]
        else:
            items = list(value)
        if not items:
            msg = "TILDA_FEED_UIDS должен содержать хотя бы одно значение"
            raise ValueError(msg)
        return tuple(items)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    env_file = os.getenv("ASKBRAIN_ENV_FILE")
    if env_file:
        candidate = Path(env_file)
        env_path = candidate if candidate.is_absolute() else Path.cwd() / candidate
    else:
        env_path = Path(__file__).resolve().parents[2] / ".env"

    if env_path.exists():
        return Settings.model_validate(dict(dotenv_values(env_path)))

    return Settings.model_validate(os.environ)

