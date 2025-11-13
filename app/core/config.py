from functools import lru_cache
from typing import List
import json

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, EnvSettingsSource


class SafeEnvSettingsSource(EnvSettingsSource):
    """Environment source that tolerates non-JSON values for complex fields."""

    def decode_complex_value(self, field_name, field, value):  # type: ignore[override]
        try:
            return super().decode_complex_value(field_name, field, value)
        except json.JSONDecodeError:
            if isinstance(value, (bytes, bytearray)):
                value = value.decode()
            return value


class Settings(BaseSettings):
    app_env: str = "dev"
    app_port: int = 8080
    supabase_url: AnyHttpUrl
    supabase_anon_key: str
    allowed_origins: List[AnyHttpUrl] = Field(default_factory=list)
    jwt_cookie_name: str = "sb-access-token"
    refresh_cookie_name: str = "sb-refresh-token"
    log_level: str = "INFO"
    rate_limit: str = "100/minute"
    request_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            SafeEnvSettingsSource(settings_cls=settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | List[str] | None):
        if value in (None, ""):
            return []

        if isinstance(value, list):
            return value

        value = value.strip()
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(",") if item.strip()]

        if isinstance(parsed, list):
            return parsed

        if isinstance(parsed, str):
            return [parsed]

        return []


@lru_cache()
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
