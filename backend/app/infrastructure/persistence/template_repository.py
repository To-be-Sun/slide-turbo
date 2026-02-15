"""
Template リポジトリ — Prisma 経由の永続化実装
"""

from __future__ import annotations

import json
from typing import Any

from prisma import Json
from prisma.models import Template as PrismaTemplate

from app.core.db import db
from app.domain.template.entity import Template


def _ensure_json_serializable(obj: Any) -> Any:
    """Prisma Json 用に JSON 互換の dict/list に正規化する"""
    return json.loads(json.dumps(obj, default=str))


def _to_entity(record: PrismaTemplate) -> Template:
    raw = record.contents
    if isinstance(raw, str):
        raw = json.loads(raw) if raw.strip() else {}
    return Template(
        id=record.id,
        owner_id=record.ownerId,
        title=record.title,
        contents=raw,
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


class TemplateRepository:
    async def create(
        self, *, owner_id: str, title: str, contents: Any
    ) -> Template:
        contents_normalized = _ensure_json_serializable(contents)
        contents_json = json.dumps(contents_normalized)
        record = await db.template.create(
            data={
                "title": title,
                "contents": contents_json,
                "owner": {"connect": {"id": owner_id}},
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
            data["contents"] = json.dumps(_ensure_json_serializable(contents))
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
