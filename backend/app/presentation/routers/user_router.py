"""
User Router — Google OAuth 認証 + ユーザー管理エンドポイント
"""

from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

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
    """Google OAuth 認証画面へリダイレクト（client_id 未設定時はログイン画面に戻す）"""
    if not settings.google_client_id:
        login_url = f"{settings.frontend_url}/login?authError=missing_client_id"
        return RedirectResponse(url=login_url, status_code=302)
    redirect_uri_encoded = quote(settings.google_redirect_uri, safe="")
    params = (
        f"client_id={settings.google_client_id}"
        f"&redirect_uri={redirect_uri_encoded}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/v2/auth?{params}",
        status_code=302,
    )


@router.get("/auth/google/refresh-token")
async def google_refresh_token_redirect():
    """
    Google Slides/Drive 用のリフレッシュトークン取得フローを開始。
    この URL にアクセス → Google で認可 → コールバックで refresh_token を表示。
    """
    if not settings.google_client_id:
        login_url = f"{settings.frontend_url}/login?authError=missing_client_id"
        return RedirectResponse(url=login_url, status_code=302)
    scopes = (
        "openid email profile "
        "https://www.googleapis.com/auth/presentations.readonly "
        "https://www.googleapis.com/auth/drive.readonly"
    )
    redirect_uri_encoded = quote(settings.google_refresh_callback_uri, safe="")
    scope_encoded = quote(scopes, safe="")
    params = (
        f"client_id={settings.google_client_id}"
        f"&redirect_uri={redirect_uri_encoded}"
        f"&response_type=code"
        f"&scope={scope_encoded}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/v2/auth?{params}",
        status_code=302,
    )


@router.get("/auth/google/refresh-callback", response_class=HTMLResponse)
async def google_refresh_token_callback(code: str | None = None, error: str | None = None):
    """
    リフレッシュトークン取得フローのコールバック。
    code をトークンに交換し、refresh_token を画面に表示する。
    """
    import httpx

    if error or not code:
        return _refresh_token_html(
            success=False,
            message=f"認証がキャンセルされたかエラーです。error={error!r}",
        )
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_refresh_callback_uri,
                "grant_type": "authorization_code",
            },
        )
    if token_resp.status_code != 200:
        return _refresh_token_html(
            success=False,
            message=f"トークン取得に失敗しました: {token_resp.text}",
        )
    try:
        tokens = token_resp.json()
    except Exception:
        tokens = {}
    refresh_token = tokens.get("refresh_token", "")
    if not refresh_token:
        return _refresh_token_html(
            success=False,
            message="レスポンスに refresh_token が含まれていません。prompt=consent で再試行するか、一度アプリのアクセスを解除してから再度認可してください。",
        )
    return _refresh_token_html(success=True, refresh_token=refresh_token)


def _refresh_token_html(*, success: bool, refresh_token: str = "", message: str = "") -> str:
    if success:
        body = f"""
        <h2>リフレッシュトークンを取得しました</h2>
        <p>以下の値をコピーし、.env の <code>GOOGLE_REFRESH_TOKEN=</code> の右に貼り付けてください。</p>
        <pre style="background:#f0f0f0; padding:1em; overflow:auto;">{refresh_token}</pre>
        <p>保存したらバックエンドを再起動してください。</p>
        """
    else:
        body = f"<h2>エラー</h2><p>{message}</p>"
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Google リフレッシュトークン</title></head>
    <body style="font-family:sans-serif; max-width:640px; margin:2em auto; padding:0 1em;">
    {body}
    </body></html>
    """


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
