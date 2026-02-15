"""
Template UseCases
テンプレートの登録・一覧取得・Google Slides からのインポート。
LLM によるテンプレート解読（スロット抽出）をサポート。
"""

import asyncio
import json
import logging
from typing import Any

from app.application.template.dto import (
    CreateTemplateDTO,
    ImportFromGoogleSlidesDTO,
    TemplateListItemDTO,
    TemplateResponseDTO,
    UpdateTemplateDTO,
)
from app.domain.template.service import TemplateService
from app.infrastructure.google_slides.parser import GoogleSlidesParser
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.shared.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class TemplateUseCases:
    def __init__(
        self,
        repo: TemplateRepository,
        slides_parser: GoogleSlidesParser,
        slides_client=None,
    ):
        self.repo = repo
        self.slides_parser = slides_parser
        self._slides_client = slides_client
        self.service = TemplateService()

    def _get_first_slide_thumbnail_url(self, contents: Any) -> str | None:
        """contents から presentationId と 1 ページ目の pageObjectId を抽出しサムネイル URL を取得。"""
        if not isinstance(contents, dict) or not self._slides_client:
            return None
        presentation_id = contents.get("presentationId")
        pages = contents.get("pages")
        if not isinstance(presentation_id, str) or not isinstance(pages, list) or not pages:
            return None
        first_page = pages[0]
        if not isinstance(first_page, dict):
            return None
        page_object_id = first_page.get("pageObjectId")
        if not isinstance(page_object_id, str):
            return None
        try:
            return self._slides_client.get_slide_thumbnail(presentation_id, page_object_id) or None
        except Exception:
            return None

    async def create(
        self, owner_id: str, dto: CreateTemplateDTO
    ) -> TemplateResponseDTO:
        """テンプレートを手動登録"""
        if not self.service.validate_contents(dto.contents):
            raise ValidationException("Invalid template contents")

        template = await self.repo.create(
            owner_id=owner_id,
            title=dto.title,
            contents=dto.contents,
        )
        return TemplateResponseDTO(
            id=template.id,
            owner_id=template.owner_id,
            title=template.title,
            contents=template.contents,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def import_from_google_slides(
        self, owner_id: str, dto: ImportFromGoogleSlidesDTO
    ) -> TemplateResponseDTO:
        """Google Slides からテンプレートをインポート（LLM 解読でスロット抽出）"""
        logger.info("import_from_google_slides: parsing url=%s", dto.presentation_url)
        parsed = await self.slides_parser.parse(dto.presentation_url)
        logger.info("import_from_google_slides: parsed title=%s", parsed.get("title"))
        title = str(parsed.get("title") or "Untitled")
        raw_contents = parsed.get("contents") or {}
        contents = json.loads(json.dumps(raw_contents, default=str))

        # LLM でテンプレート解読（編集可能スロット抽出・非同期でブロック回避）
        try:
            from app.infrastructure.ai.template_interpreter import interpret_template
            slots = await asyncio.to_thread(interpret_template, contents)
            if slots:
                contents["slots"] = slots
                logger.info("import_from_google_slides: %d slots extracted by LLM", len(slots))
        except Exception as e:
            logger.warning("Template interpretation skipped: %s", e)

        template = await self.repo.create(
            owner_id=owner_id,
            title=title,
            contents=contents,
        )
        return TemplateResponseDTO(
            id=template.id,
            owner_id=template.owner_id,
            title=template.title,
            contents=template.contents,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def list_by_owner(self, owner_id: str) -> list[TemplateListItemDTO]:
        """オーナーのテンプレート一覧"""
        templates = await self.repo.find_by_owner(owner_id)
        return [
            TemplateListItemDTO(id=t.id, title=t.title, created_at=t.created_at)
            for t in templates
        ]

    async def get_by_id(self, template_id: str) -> TemplateResponseDTO:
        """テンプレート詳細取得"""
        template = await self.repo.find_by_id(template_id)
        if template is None:
            raise NotFoundException("Template", template_id)
        return TemplateResponseDTO(
            id=template.id,
            owner_id=template.owner_id,
            title=template.title,
            contents=template.contents,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def update(
        self, template_id: str, dto: UpdateTemplateDTO
    ) -> TemplateResponseDTO:
        """テンプレート更新"""
        template = await self.repo.update(
            template_id, title=dto.title, contents=dto.contents
        )
        if template is None:
            raise NotFoundException("Template", template_id)
        return TemplateResponseDTO(
            id=template.id,
            owner_id=template.owner_id,
            title=template.title,
            contents=template.contents,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    async def delete(self, template_id: str) -> None:
        """テンプレート削除"""
        deleted = await self.repo.delete(template_id)
        if not deleted:
            raise NotFoundException("Template", template_id)

    def _get_all_slide_thumbnail_urls(self, contents: Any) -> list[str]:
        """contents の全ページについてサムネイル URL を取得。"""
        if not isinstance(contents, dict) or not self._slides_client:
            return []
        presentation_id = contents.get("presentationId")
        pages = contents.get("pages")
        if not isinstance(presentation_id, str) or not isinstance(pages, list):
            return []
        urls: list[str] = []
        for page in pages:
            if not isinstance(page, dict):
                continue
            page_object_id = page.get("pageObjectId")
            if not isinstance(page_object_id, str):
                continue
            try:
                url = self._slides_client.get_slide_thumbnail(
                    presentation_id, page_object_id
                )
                if url:
                    urls.append(url)
            except Exception:
                pass
        return urls

    async def get_thumbnail_url(self, template_id: str) -> str | None:
        """テンプレート 1 ページ目のサムネイル URL を取得（Google Slides インポートのみ対応）。"""
        template = await self.repo.find_by_id(template_id)
        if template is None:
            return None
        return self._get_first_slide_thumbnail_url(template.contents)

    async def get_all_thumbnail_urls(self, template_id: str) -> list[str]:
        """テンプレート全ページのサムネイル URL を取得（Google Slides インポートのみ対応）。"""
        template = await self.repo.find_by_id(template_id)
        if template is None:
            return []
        return self._get_all_slide_thumbnail_urls(template.contents)
