"""
Outline (骨子) UseCases
骨子の CRUD と AI によるブラッシュアップ。
"""

from app.application.outline.dto import (
    CreateOutlineDTO,
    GenerateSlideFromOutlineDTO,
    OutlineResponseDTO,
    RefineOutlineDTO,
    SlideOutputResponseDTO,
    UpdateOutlineDTO,
)
from app.domain.outline.service import OutlineService
from app.infrastructure.ai.multi_agent_slide_generator import (
    MultiAgentSlideGenerator,
)
from app.infrastructure.persistence.outline_repository import OutlineRepository
from app.shared.exceptions import NotFoundException, ValidationException


class OutlineUseCases:
    def __init__(self, repo: OutlineRepository):
        self.repo = repo
        self.service = OutlineService()
        self.slide_generator = MultiAgentSlideGenerator()

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

    async def generate_slide(
        self, dto: GenerateSlideFromOutlineDTO
    ) -> SlideOutputResponseDTO:
        """骨子から1枚スライドJSONを multi-agent で生成"""
        outline = await self.repo.find_by_id(dto.outline_id)
        if outline is None:
            raise NotFoundException("Outline", dto.outline_id)
        all_outlines = await self.repo.find_by_version(outline.slide_version_id)
        outlines_context = [
            {
                "id": o.id,
                "title": o.title,
                "description": o.description,
            }
            for o in all_outlines
        ]
        outline_index = next(
            (i for i, o in enumerate(all_outlines) if o.id == outline.id),
            0,
        )
        inferred_page_num = outline_index + 1
        effective_page_num = dto.page_num if (dto.page_num and dto.page_num > 0) else inferred_page_num
        effective_total_pages = max(
            len(all_outlines),
            dto.total_pages if (dto.total_pages and dto.total_pages > 0) else len(all_outlines),
        )

        slide = await self.slide_generator.generate_one_slide(
            title=outline.title,
            description=outline.description,
            slide_id=dto.slide_object_id,
            image_url=dto.image_url,
            page_num=effective_page_num,
            total_pages=effective_total_pages,
            previous_slide_summary=dto.previous_slide_summary,
            current_outline_id=outline.id,
            outlines_context=outlines_context,
        )
        return SlideOutputResponseDTO(
            outline_id=outline.id,
            slide=slide,
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
