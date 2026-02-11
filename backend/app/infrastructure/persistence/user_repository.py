"""
User リポジトリ — Prisma 経由の永続化実装
"""

from __future__ import annotations

from prisma.models import User as PrismaUser

from app.core.db import db
from app.domain.user.entity import User


def _to_entity(record: PrismaUser) -> User:
    return User(
        id=record.id,
        email=record.email,
        name=record.name,
        icon=record.icon,
        google_id=record.googleId,
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


class UserRepository:
    async def create(
        self, *, email: str, name: str, icon: str | None, google_id: str
    ) -> User:
        record = await db.user.create(
            data={
                "email": email,
                "name": name,
                "icon": icon,
                "googleId": google_id,
            }
        )
        return _to_entity(record)

    async def find_by_id(self, user_id: str) -> User | None:
        record = await db.user.find_unique(where={"id": user_id})
        return _to_entity(record) if record else None

    async def find_by_google_id(self, google_id: str) -> User | None:
        record = await db.user.find_unique(where={"googleId": google_id})
        return _to_entity(record) if record else None

    async def find_by_email(self, email: str) -> User | None:
        record = await db.user.find_unique(where={"email": email})
        return _to_entity(record) if record else None

    async def update(
        self, user_id: str, *, name: str | None = None, icon: str | None = None
    ) -> User | None:
        data: dict = {}
        if name is not None:
            data["name"] = name
        if icon is not None:
            data["icon"] = icon
        if not data:
            return await self.find_by_id(user_id)
        record = await db.user.update(where={"id": user_id}, data=data)
        return _to_entity(record) if record else None
