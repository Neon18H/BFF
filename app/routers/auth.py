from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from app.core.config import Settings, get_settings
from app.core.security import AuthContext, clear_auth_cookies, get_auth_context, set_auth_cookies
from app.db.supabase_client import SupabaseClient, get_supabase_client
from app.models.auth import AuthResponse, MeResponse, SignInRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(supabase: SupabaseClient = Depends(get_supabase_client)) -> AuthService:
    return AuthService(supabase)


@router.post("/signin", response_model=AuthResponse)
async def signin(
    payload: SignInRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    auth = await service.sign_in(payload.email, payload.password)
    set_auth_cookies(response, auth.access_token, auth.refresh_token, settings)
    return auth


@router.post(
    "/signout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def signout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> None:
    token = request.cookies.get(settings.jwt_cookie_name)
    await service.sign_out(token)
    clear_auth_cookies(response, settings)


@router.get("/me", response_model=MeResponse)
async def me(
    auth: AuthContext = Depends(get_auth_context),
    service: AuthService = Depends(get_auth_service),
) -> MeResponse:
    user = await service.me(auth.access_token)
    return MeResponse(user=user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    auth = await service.refresh(refresh_token or "")
    set_auth_cookies(response, auth.access_token, auth.refresh_token, settings)
    return auth
