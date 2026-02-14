"""
User UseCases
Google OAuth ログイン・プロフィール取得。
"""

from __future__ import annotations

from app.application.user.dto import (
    GoogleLoginDTO,
    TokenResponseDTO,
    UpdateUserDTO,
    UserResponseDTO,
)
from app.core.security import create_access_token
from app.infrastructure.persistence.user_repository import UserRepository
from app.shared.exceptions import NotFoundException


class UserUseCases:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def google_login(
        self,
        google_id: str,
        email: str,
        name: str,
        icon: str | None,
        google_access_token: str | None = None,
    ) -> TokenResponseDTO:
        """
        Google OAuth コールバック後の処理。
        ユーザーが存在すれば取得、なければ新規作成して JWT を発行する。
        """
        user = await self.repo.find_by_google_id(google_id)

        if user is None:
            user = await self.repo.create(
                email=email,
                name=name,
                icon=icon,
                google_id=google_id,
            )

        token = create_access_token(data={"sub": user.id})
        return TokenResponseDTO(
            access_token=token,
            google_access_token=google_access_token,
            user=UserResponseDTO(
                id=user.id,
                email=user.email,
                name=user.name,
                icon=user.icon,
                created_at=user.created_at,
            ),
        )

    async def get_me(self, user_id: str) -> UserResponseDTO:
        """現在ログイン中のユーザー情報を取得"""
        user = await self.repo.find_by_id(user_id)
        if user is None:
            raise NotFoundException("User", user_id)
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            name=user.name,
            icon=user.icon,
            created_at=user.created_at,
        )

    async def update(self, user_id: str, dto: UpdateUserDTO) -> UserResponseDTO:
        """プロフィール更新"""
        user = await self.repo.update(user_id, name=dto.name, icon=dto.icon)
        if user is None:
            raise NotFoundException("User", user_id)
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            name=user.name,
            icon=user.icon,
            created_at=user.created_at,
        )
