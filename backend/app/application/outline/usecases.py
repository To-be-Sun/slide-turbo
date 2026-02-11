"""
Outline (骨子) UseCases
骨子の CRUD と AI によるブラッシュアップ。
"""

from app.application.outline.dto import (
    CreateOutlineDTO,
    OutlineResponseDTO,
    RefineOutlineDTO,
    UpdateOutlineDTO,
)
from app.domain.outline.service import OutlineService
from app.infrastructure.persistence.outline_repository import OutlineRepository
from app.shared.exceptions import NotFoundException, ValidationException


class OutlineUseCases:
    def __init__(self, repo: OutlineRepository):
        self.repo = repo
        self.service = OutlineService()

    async def create(self, dto: CreateOutlineDTO) -> OutlineResponseDTO:
        """骨子を新規作成"""
        if not self.service.validate_outline(dto.title, dto.description):
            raise ValidationException("Title and description are required")

        outline = await self.repo.create(
            slide_version_id=dto.slide_version_id,
            title=dto.title,
            description=dto.description,
        )
        return OutlineResponseDTO(
            id=outline.id,
            slide_version_id=outline.slide_version_id,
            title=outline.title,
            description=outline.description,
            created_at=outline.created_at,
            updated_at=outline.updated_at,
        )

    async def list_by_version(
        self, slide_version_id: str
    ) -> list[OutlineResponseDTO]:
        """バージョンに紐づく骨子一覧"""
        outlines = await self.repo.find_by_version(slide_version_id)
        return [
            OutlineResponseDTO(
                id=o.id,
                slide_version_id=o.slide_version_id,
                title=o.title,
                description=o.description,
                created_at=o.created_at,
                updated_at=o.updated_at,
            )
            for o in outlines
        ]

    async def get_by_id(self, outline_id: str) -> OutlineResponseDTO:
        """骨子詳細取得"""
        outline = await self.repo.find_by_id(outline_id)
        if outline is None:
            raise NotFoundException("Outline", outline_id)
        return OutlineResponseDTO(
            id=outline.id,
            slide_version_id=outline.slide_version_id,
            title=outline.title,
            description=outline.description,
            created_at=outline.created_at,
            updated_at=outline.updated_at,
        )

    async def update(
        self, outline_id: str, dto: UpdateOutlineDTO
    ) -> OutlineResponseDTO:
        """骨子更新"""
        outline = await self.repo.update(
            outline_id, title=dto.title, description=dto.description
        )
        if outline is None:
            raise NotFoundException("Outline", outline_id)
        return OutlineResponseDTO(
            id=outline.id,
            slide_version_id=outline.slide_version_id,
            title=outline.title,
            description=outline.description,
            created_at=outline.created_at,
            updated_at=outline.updated_at,
        )

    async def delete(self, outline_id: str) -> None:
        """骨子削除"""
        deleted = await self.repo.delete(outline_id)
        if not deleted:
            raise NotFoundException("Outline", outline_id)

    async def refine(self, dto: RefineOutlineDTO) -> OutlineResponseDTO:
        """
        マルチエージェントで骨子をブラッシュアップ
        TODO: infrastructure/ai のオーケストレーターを呼び出す
        """
        outline = await self.repo.find_by_id(dto.outline_id)
        if outline is None:
            raise NotFoundException("Outline", dto.outline_id)

        # TODO: AI エージェント呼び出し
        # refined = await self.ai_service.refine_outline(outline, dto.instructions)
        # outline = await self.repo.update(outline.id, ...)

        return OutlineResponseDTO(
            id=outline.id,
            slide_version_id=outline.slide_version_id,
            title=outline.title,
            description=outline.description,
            created_at=outline.created_at,
            updated_at=outline.updated_at,
        )
