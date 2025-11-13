import pytest

from app.core.config import Settings


@pytest.fixture(autouse=True)
def required_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-key")
    yield
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)


def test_allowed_origins_handles_empty_string(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "")

    settings = Settings()

    assert settings.allowed_origins == []


def test_allowed_origins_parses_comma_separated(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000, https://example.com",
    )

    settings = Settings()

    assert [str(origin).rstrip("/") for origin in settings.allowed_origins] == [
        "http://localhost:3000",
        "https://example.com",
    ]
