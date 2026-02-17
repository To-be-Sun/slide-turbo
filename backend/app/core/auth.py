"""
認証の FastAPI Dependency
各 router で Depends(get_current_user) として使用する。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_token
from app.core.db import db
from app.core.config import settings

security_scheme = HTTPBearer()

# 開発用トークン
DEV_TOKEN = "dev-token-slide-turbo"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    """
    JWT トークンを検証し、現在ログイン中の User を返す。
    開発環境では dev-token-slide-turbo も許可する。

    Raises:
        HTTPException 401: トークン不正 or ユーザー不存在
    """
    # 開発環境でdev-tokenの場合
    if settings.env == "development" and credentials.credentials == DEV_TOKEN:
        # 開発用ユーザーをDBから取得（なければ最初のユーザーを使用）
        dev_user = await db.user.find_first()
        if dev_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No user in database. Please login with Google first.",
            )
        return dev_user

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = await db.user.find_unique(where={"id": payload["sub"]})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
