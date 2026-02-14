"""
Template リポジトリ — Prisma 経由の永続化実装
"""

from __future__ import annotations

from typing import Any

from prisma import Json
from prisma.models import Template as PrismaTemplate

from app.core.db import db
from app.domain.template.entity import Template


def _to_entity(record: PrismaTemplate) -> Template:
    return Template(
        id=record.id,
        owner_id=record.ownerId,
        title=record.title,
        contents=record.contents,
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


class TemplateRepository:
    async def create(
        self, *, owner_id: str, title: str, contents: Any
    ) -> Template:
        record = await db.template.create(
            data={
                "owner": {"connect": {"id": owner_id}},
                "title": title,
                "contents": Json(contents),
            }
        )
        return _to_entity(record)

    async def find_by_id(self, template_id: str) -> Template | None:
        record = await db.template.find_unique(where={"id": template_id})
        return _to_entity(record) if record else None

    async def find_by_owner(self, owner_id: str) -> list[Template]:
        records = await db.template.find_many(
            where={"ownerId": owner_id},
            order={"createdAt": "desc"},
        )
        return [_to_entity(r) for r in records]

    async def update(
        self,
        template_id: str,
        *,
        title: str | None = None,
        contents: Any | None = None,
    ) -> Template | None:
        data: dict = {}
        if title is not None:
            data["title"] = title
        if contents is not None:
            data["contents"] = contents
        if not data:
            return await self.find_by_id(template_id)
        record = await db.template.update(
            where={"id": template_id}, data=data
        )
        return _to_entity(record) if record else None

    async def delete(self, template_id: str) -> bool:
        try:
            await db.template.delete(where={"id": template_id})
            return True
        except Exception:
            return False
