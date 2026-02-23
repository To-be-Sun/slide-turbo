"""
Slide / SlideVersion / Page リポジトリ — Prisma 経由の永続化実装
"""

from __future__ import annotations

from typing import Any

from prisma import Json
from prisma.models import Page as PrismaPage
from prisma.models import Slide as PrismaSlide
from prisma.models import SlideVersion as PrismaSlideVersion

from app.core.db import db
from app.domain.slide.entity import Page, Slide, SlideVersion


# ── Converters ────────────────────────────────────────


def _to_slide(record: PrismaSlide) -> Slide:
    return Slide(
        id=record.id,
        owner_id=record.ownerId,
        template_id=record.templateId,
        title=record.title,
        images=record.images or [],
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


def _to_version(record: PrismaSlideVersion) -> SlideVersion:
    return SlideVersion(
        id=record.id,
        slide_id=record.slideId,
        version_num=record.versionNum,
        created_at=record.createdAt,
    )


def _to_page(record: PrismaPage) -> Page:
    return Page(
        id=record.id,
        slide_version_id=record.slideVersionId,
        page_num=record.pageNum,
        contents=record.contents,
        created_at=record.createdAt,
        updated_at=record.updatedAt,
    )


class SlideRepository:
    # ── Slide ─────────────────────────────────────────

    async def create_slide(
        self,
        *,
        owner_id: str,
        title: str,
        template_id: str | None = None,
    ) -> Slide:
        data: dict[str, Any] = {
            "ownerId": owner_id,
            "title": title,
        }
        if template_id:
            data["templateId"] = template_id
        record = await db.slide.create(data=data)
        return _to_slide(record)

    async def find_slide_by_id(self, slide_id: str) -> Slide | None:
        record = await db.slide.find_unique(where={"id": slide_id})
        return _to_slide(record) if record else None

    async def find_slides_by_owner(self, owner_id: str) -> list[Slide]:
        records = await db.slide.find_many(
            where={"ownerId": owner_id},
            order={"updatedAt": "desc"},
        )
        return [_to_slide(r) for r in records]

    async def update_slide(
        self, slide_id: str, *, title: str | None = None
    ) -> Slide | None:
        data: dict = {}
        if title is not None:
            data["title"] = title
        if not data:
            return await self.find_slide_by_id(slide_id)
        record = await db.slide.update(where={"id": slide_id}, data=data)
        return _to_slide(record) if record else None

    async def delete_slide(self, slide_id: str) -> bool:
        try:
            await db.slide.delete(where={"id": slide_id})
            return True
        except Exception:
            return False

    # ── SlideVersion ──────────────────────────────────

    async def create_version(
        self, *, slide_id: str, version_num: int
    ) -> SlideVersion:
        record = await db.slideversion.create(
            data={"slideId": slide_id, "versionNum": version_num}
        )
        return _to_version(record)

    async def find_latest_version(
        self, slide_id: str
    ) -> SlideVersion | None:
        record = await db.slideversion.find_first(
            where={"slideId": slide_id},
            order={"versionNum": "desc"},
        )
        return _to_version(record) if record else None

    async def find_versions_by_slide(
        self, slide_id: str
    ) -> list[SlideVersion]:
        records = await db.slideversion.find_many(
            where={"slideId": slide_id},
            order={"versionNum": "asc"},
        )
        return [_to_version(r) for r in records]

    # ── Page ──────────────────────────────────────────

    async def create_page(
        self,
        *,
        slide_version_id: str,
        page_num: int,
        contents: Any,
    ) -> Page:
        record = await db.page.create(
            data={
                "slideVersionId": slide_version_id,
                "pageNum": page_num,
                "contents": Json(contents),
            }
        )
        return _to_page(record)

    async def find_pages_by_version(
        self, version_id: str
    ) -> list[Page]:
        records = await db.page.find_many(
            where={"slideVersionId": version_id},
            order={"pageNum": "asc"},
        )
        return [_to_page(r) for r in records]

    async def find_page_by_id(self, page_id: str) -> Page | None:
        record = await db.page.find_unique(where={"id": page_id})
        return _to_page(record) if record else None

    async def update_page(
        self, page_id: str, *, contents: Any
    ) -> Page | None:
        record = await db.page.update(
            where={"id": page_id},
            data={"contents": Json(contents)},
        )
        return _to_page(record) if record else None

    async def update_page_num(
        self, page_id: str, *, page_num: int
    ) -> Page | None:
        record = await db.page.update(
            where={"id": page_id},
            data={"pageNum": page_num},
        )
        return _to_page(record) if record else None

    async def delete_page(self, page_id: str) -> bool:
        try:
            await db.page.delete(where={"id": page_id})
            return True
        except Exception:
            return False
