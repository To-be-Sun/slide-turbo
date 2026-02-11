"""
User Router — Google OAuth 認証 + ユーザー管理エンドポイント
"""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.application.user.dto import (
    GoogleLoginDTO,
    TokenResponseDTO,
    UpdateUserDTO,
    UserResponseDTO,
)
from app.application.user.usecases import UserUseCases
from app.core.auth import get_current_user
from app.core.config import settings
from app.infrastructure.persistence.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


def _get_usecases() -> UserUseCases:
    return UserUseCases(repo=UserRepository())


# ── Google OAuth ──────────────────────────────────────


@router.get("/auth/google")
async def google_auth_redirect():
    """Google OAuth 認証画面へリダイレクト"""
    params = (
        f"client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    )


@router.post("/auth/google/callback", response_model=TokenResponseDTO)
async def google_auth_callback(
    body: GoogleLoginDTO,
    uc: UserUseCases = Depends(_get_usecases),
):
    """
    Google OAuth コールバック。
    認可コードを受け取り、Google からユーザー情報を取得して JWT を発行する。

    TODO: httpx で Google token endpoint を叩いて id_token を検証する
    """
    import httpx

    # 1. 認可コード → トークン交換
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": body.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        tokens = token_resp.json()

    # 2. id_token からユーザー情報を取得
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        userinfo = userinfo_resp.json()

    # 3. ユーザー作成 or 取得 → JWT 発行
    return await uc.google_login(
        google_id=userinfo["sub"],
        email=userinfo["email"],
        name=userinfo.get("name", ""),
        icon=userinfo.get("picture"),
    )


# ── User Profile ──────────────────────────────────────


@router.get("/me", response_model=UserResponseDTO)
async def get_me(
    current_user=Depends(get_current_user),
    uc: UserUseCases = Depends(_get_usecases),
):
    """現在ログイン中のユーザー情報"""
    return await uc.get_me(current_user.id)


@router.patch("/me", response_model=UserResponseDTO)
async def update_me(
    body: UpdateUserDTO,
    current_user=Depends(get_current_user),
    uc: UserUseCases = Depends(_get_usecases),
):
    """プロフィール更新"""
    return await uc.update(current_user.id, body)
