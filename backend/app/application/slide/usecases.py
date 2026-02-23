"""
Slide (Project) UseCases
スライドの CRUD、バージョン管理、ページ操作、HTMLレンダリング、Google Slidesエクスポート。
"""

from app.application.slide.dto import (
    CreatePageDTO,
    CreateSlideDTO,
    PageResponseDTO,
    SlideListItemDTO,
    SlideResponseDTO,
    SlideVersionResponseDTO,
    UpdatePageDTO,
    UpdateSlideDTO,
)
from app.domain.slide.service import SlideService
from app.infrastructure.persistence.slide_repository import SlideRepository
from app.infrastructure.rendering.html_renderer import HTMLRenderer
from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
from app.shared.exceptions import NotFoundException


class SlideUseCases:
    def __init__(self, repo: SlideRepository):
        self.repo = repo
        self.service = SlideService()

    # ── Slide CRUD ────────────────────────────────────

    async def create(
        self, owner_id: str, dto: CreateSlideDTO
    ) -> SlideResponseDTO:
        """新規スライドプロジェクト作成 + version 1 を自動生成"""
        slide = await self.repo.create_slide(
            owner_id=owner_id,
            title=dto.title,
            template_id=dto.template_id,
        )
        # version 1 を自動生成
        await self.repo.create_version(slide_id=slide.id, version_num=1)

        return SlideResponseDTO(
            id=slide.id,
            owner_id=slide.owner_id,
            template_id=slide.template_id,
            title=slide.title,
            images=slide.images,
            created_at=slide.created_at,
            updated_at=slide.updated_at,
        )

    async def list_by_owner(self, owner_id: str) -> list[SlideListItemDTO]:
        """オーナーのスライド一覧"""
        slides = await self.repo.find_slides_by_owner(owner_id)
        return [
            SlideListItemDTO(
                id=s.id,
                title=s.title,
                template_id=s.template_id,
                images=s.images,
                updated_at=s.updated_at,
            )
            for s in slides
        ]

    async def get_by_id(self, slide_id: str) -> SlideResponseDTO:
        """スライド詳細取得"""
        slide = await self.repo.find_slide_by_id(slide_id)
        if slide is None:
            raise NotFoundException("Slide", slide_id)
        return SlideResponseDTO(
            id=slide.id,
            owner_id=slide.owner_id,
            template_id=slide.template_id,
            title=slide.title,
            images=slide.images,
            created_at=slide.created_at,
            updated_at=slide.updated_at,
        )

    async def update(
        self, slide_id: str, dto: UpdateSlideDTO
    ) -> SlideResponseDTO:
        """スライド更新"""
        slide = await self.repo.update_slide(slide_id, title=dto.title)
        if slide is None:
            raise NotFoundException("Slide", slide_id)
        return SlideResponseDTO(
            id=slide.id,
            owner_id=slide.owner_id,
            template_id=slide.template_id,
            title=slide.title,
            images=slide.images,
            created_at=slide.created_at,
            updated_at=slide.updated_at,
        )

    async def delete(self, slide_id: str) -> None:
        """スライド削除 (CASCADE で version, page, outline も削除)"""
        deleted = await self.repo.delete_slide(slide_id)
        if not deleted:
            raise NotFoundException("Slide", slide_id)

    # ── Version ───────────────────────────────────────

    async def create_version(self, slide_id: str) -> SlideVersionResponseDTO:
        """新バージョンを作成"""
        latest = await self.repo.find_latest_version(slide_id)
        next_num = self.service.next_version_num(
            latest.version_num if latest else 0
        )
        version = await self.repo.create_version(
            slide_id=slide_id, version_num=next_num
        )
        return SlideVersionResponseDTO(
            id=version.id,
            slide_id=version.slide_id,
            version_num=version.version_num,
            created_at=version.created_at,
        )

    async def list_versions(
        self, slide_id: str
    ) -> list[SlideVersionResponseDTO]:
        """バージョン一覧"""
        versions = await self.repo.find_versions_by_slide(slide_id)
        return [
            SlideVersionResponseDTO(
                id=v.id,
                slide_id=v.slide_id,
                version_num=v.version_num,
                created_at=v.created_at,
            )
            for v in versions
        ]

    # ── Page ──────────────────────────────────────────

    async def add_page(
        self, version_id: str, dto: CreatePageDTO
    ) -> PageResponseDTO:
        """ページ追加"""
        # page_num 衝突時は末尾へ自動採番して Unique 制約違反を回避する
        pages = await self.repo.find_pages_by_version(version_id)
        existing_nums = {p.page_num for p in pages}
        page_num = dto.page_num
        if page_num in existing_nums:
            page_num = (max(existing_nums) if existing_nums else 0) + 1

        page = await self.repo.create_page(
            slide_version_id=version_id,
            page_num=page_num,
            contents=dto.contents,
        )
        return PageResponseDTO(
            id=page.id,
            slide_version_id=page.slide_version_id,
            page_num=page.page_num,
            contents=page.contents,
            created_at=page.created_at,
            updated_at=page.updated_at,
        )

    async def update_page(
        self, page_id: str, dto: UpdatePageDTO
    ) -> PageResponseDTO:
        """ページ更新"""
        page = await self.repo.update_page(page_id, contents=dto.contents)
        if page is None:
            raise NotFoundException("Page", page_id)
        return PageResponseDTO(
            id=page.id,
            slide_version_id=page.slide_version_id,
            page_num=page.page_num,
            contents=page.contents,
            created_at=page.created_at,
            updated_at=page.updated_at,
        )

    async def list_pages(self, version_id: str) -> list[PageResponseDTO]:
        """バージョン内のページ一覧 (pageNum 昇順)"""
        pages = await self.repo.find_pages_by_version(version_id)
        return [
            PageResponseDTO(
                id=p.id,
                slide_version_id=p.slide_version_id,
                page_num=p.page_num,
                contents=p.contents,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in pages
        ]

    async def delete_page(self, page_id: str) -> None:
        """ページ削除"""
        page = await self.repo.find_page_by_id(page_id)
        if page is None:
            raise NotFoundException("Page", page_id)

        deleted = await self.repo.delete_page(page_id)
        if not deleted:
            raise NotFoundException("Page", page_id)

        # 削除後に page_num を 1..N へ詰め直す
        pages = await self.repo.find_pages_by_version(page.slide_version_id)
        for index, p in enumerate(pages, start=1):
            if p.page_num != index:
                await self.repo.update_page_num(p.id, page_num=index)

    # ── Rendering & Export ────────────────────────────

    async def render_preview(self, slide_id: str, version_num: int | None = None) -> str:
        """スライドのHTMLプレビュー生成
        
        Args:
            slide_id: スライドID
            version_num: バージョン番号（Noneの場合は最新）
        
        Returns:
            HTML文字列
        """
        slide = await self.repo.find_slide_by_id(slide_id)
        if slide is None:
            raise NotFoundException("Slide", slide_id)
        
        # バージョン取得
        if version_num is None:
            version = await self.repo.find_latest_version(slide_id)
        else:
            versions = await self.repo.find_versions_by_slide(slide_id)
            version = next((v for v in versions if v.version_num == version_num), None)
        
        if version is None:
            raise NotFoundException("SlideVersion", f"{slide_id}/v{version_num or 'latest'}")
        
        # ページ取得（Google Slides API形式のcontents）
        pages = await self.repo.find_pages_by_version(version.id)
        page_data_list = [p.contents for p in pages]  # contents = dict[str, Any]
        
        # HTMLレンダリング
        renderer = HTMLRenderer()
        html = renderer.render_presentation(title=slide.title, pages=page_data_list)
        return html
    
    async def export_to_google_slides(
        self, slide_id: str, version_num: int | None = None, owner_email: str | None = None
    ) -> str:
        """Google Slidesへエクスポート
        
        Args:
            slide_id: スライドID
            version_num: バージョン番号（Noneの場合は最新）
            owner_email: Google Slidesの共有先メールアドレス
        
        Returns:
            作成されたGoogle SlidesのプレゼンテーションID
        """
        slide = await self.repo.find_slide_by_id(slide_id)
        if slide is None:
            raise NotFoundException("Slide", slide_id)
        
        # バージョン取得
        if version_num is None:
            version = await self.repo.find_latest_version(slide_id)
        else:
            versions = await self.repo.find_versions_by_slide(slide_id)
            version = next((v for v in versions if v.version_num == version_num), None)
        
        if version is None:
            raise NotFoundException("SlideVersion", f"{slide_id}/v{version_num or 'latest'}")
        
        # ページ取得（Google Slides API形式のcontents）
        pages = await self.repo.find_pages_by_version(version.id)
        page_data_list = [p.contents for p in pages]
        
        # Google Slidesエクスポート
        exporter = GoogleSlidesExporter()
        presentation_id = await exporter.create_presentation(
            title=slide.title,
            pages=page_data_list,
            owner_email=owner_email,
        )
        return presentation_id
