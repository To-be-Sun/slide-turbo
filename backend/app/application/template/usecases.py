"""
Template UseCases
テンプレートの登録・一覧取得・Google Slides からのインポート。
"""

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


class TemplateUseCases:
    def __init__(
        self,
        repo: TemplateRepository,
        slides_parser: GoogleSlidesParser,
    ):
        self.repo = repo
        self.slides_parser = slides_parser
        self.service = TemplateService()

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
        """Google Slides からテンプレートをインポート"""
        parsed = await self.slides_parser.parse(dto.presentation_url)
        template = await self.repo.create(
            owner_id=owner_id,
            title=parsed["title"],
            contents=parsed["contents"],
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
