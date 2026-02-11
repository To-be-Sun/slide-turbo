"""
Outline リポジトリ — Prisma 経由の永続化実装
"""

from __future__ import annotations

from prisma.models import Outline as PrismaOutline

from app.core.db import db
from app.domain.outline.entity import Outline


def _to_entity(record: PrismaOutline) -> Outline:
    return Outline(
        id=record.id,
        slide_version_id=record.slideVersionId,
        title=record.title,
        description=record.description,
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


class OutlineRepository:
    async def create(
        self,
        *,
        slide_version_id: str,
        title: str,
        description: str,
    ) -> Outline:
        record = await db.outline.create(
            data={
                "slideVersionId": slide_version_id,
                "title": title,
                "description": description,
            }
        )
        return _to_entity(record)

    async def find_by_id(self, outline_id: str) -> Outline | None:
        record = await db.outline.find_unique(where={"id": outline_id})
        return _to_entity(record) if record else None

    async def find_by_version(
        self, slide_version_id: str
    ) -> list[Outline]:
        records = await db.outline.find_many(
            where={"slideVersionId": slide_version_id},
            order={"createdAt": "asc"},
        )
        return [_to_entity(r) for r in records]

    async def update(
        self,
        outline_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> Outline | None:
        data: dict = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if not data:
            return await self.find_by_id(outline_id)
        record = await db.outline.update(
            where={"id": outline_id}, data=data
        )
        return _to_entity(record) if record else None

    async def delete(self, outline_id: str) -> bool:
        try:
            await db.outline.delete(where={"id": outline_id})
            return True
        except Exception:
            return False
