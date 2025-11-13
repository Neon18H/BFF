from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

import re
from ipaddress import ip_address
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.db.supabase_client import SupabaseClient
from app.routers import auth, clients, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    supabase_client = SupabaseClient(settings)
    app.state.supabase_client = supabase_client
    try:
        yield
    finally:
        await supabase_client.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
    app = FastAPI(title="Flutter BFF", version="0.1.0", lifespan=lifespan)

    app.state.limiter = limiter
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RateLimitExceeded, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.add_middleware(SlowAPIMiddleware)

    allow_origins: list[str] = []
    regex_patterns: list[str] = []

    for origin_value in settings.allowed_origins:
        origin = str(origin_value)
        parsed = urlparse(origin)
        hostname = parsed.hostname
        if not hostname or parsed.scheme not in {"http", "https"}:
            allow_origins.append(origin)
            continue

        should_allow_dynamic_port = False
        if hostname == "localhost":
            should_allow_dynamic_port = True
        else:
            try:
                ip = ip_address(hostname)
            except ValueError:
                ip = None

            if ip is not None and (ip.is_loopback or ip.is_private):
                should_allow_dynamic_port = True

        if should_allow_dynamic_port:
            escaped = re.escape(f"{parsed.scheme}://{hostname}")
            regex_patterns.append(rf"^{escaped}(?::\d+)?/?$")
            if parsed.port is not None:
                allow_origins.append(origin)
        else:
            allow_origins.append(origin)

    allow_origin_regex = None
    if regex_patterns:
        allow_origin_regex = "|".join(regex_patterns)
    elif not allow_origins:
        allow_origin_regex = ".*"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    app.include_router(auth.router)
    app.include_router(clients.router)
    app.include_router(tasks.router)

    return app


app = create_app()


__all__ = ["app", "create_app"]
