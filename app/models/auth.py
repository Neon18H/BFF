from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EmailString = Annotated[str, StringConstraints(pattern=EMAIL_PATTERN.pattern)]


class SignInRequest(BaseModel):
    email: EmailString
    password: str


class AuthUser(BaseModel):
    id: str
    email: EmailString
    role: Optional[str] = None
    last_sign_in_at: Optional[datetime] = Field(default=None, alias="lastSignInAt")

    class Config:
        populate_by_name = True


class AuthResponse(BaseModel):
    access_token: str = Field(alias="access_token")
    refresh_token: Optional[str] = Field(alias="refresh_token", default=None)
    token_type: str = Field(alias="token_type")
    expires_in: int = Field(alias="expires_in")
    user: Optional[AuthUser] = None

    class Config:
        populate_by_name = True


class MeResponse(BaseModel):
    user: AuthUser


__all__ = ["SignInRequest", "AuthResponse", "AuthUser", "MeResponse"]
