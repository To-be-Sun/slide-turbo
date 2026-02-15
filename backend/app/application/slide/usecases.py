"""
Slide (Project) UseCases
スライドの CRUD、バージョン管理、ページ操作。
"""

import html
from typing import Any

from app.application.slide.dto import (
    CreatePageDTO,
    CreateSlideDTO,
    PageResponseDTO,
    SlideListItemDTO,
    SlideResponseDTO,
    SlideVersionResponseDTO,
    SyncPageEditsDTO,
    UpdatePageDTO,
    UpdateSlideDTO,
)
from app.domain.slide.service import SlideService
from app.infrastructure.persistence.slide_repository import SlideRepository
from app.infrastructure.rendering import HTMLRenderer, SlidePresentation
from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
from app.infrastructure.persistence.template_repository import (
    TemplateRepository,
)
from app.shared.exceptions import NotFoundException


def _template_elements_to_html(elements: list[dict[str, Any]]) -> str:
    """テンプレートの elements（shape/image/shape_rect）を表示用 HTML に変換。位置・サイズ・塗りつぶしを反映。"""
    parts: list[str] = []
    has_layout = any(
        (el.get("width_pct") or 0) > 0 or (el.get("height_pct") or 0) > 0
        for el in elements
    )
    for i, el in enumerate(elements):
        el_type = el.get("type", "unknown")
        style_parts: list[str] = []
        if has_layout:
            left = el.get("left_pct")
            top = el.get("top_pct")
            w = el.get("width_pct")
            h = el.get("height_pct")
            if left is not None:
                style_parts.append(f"left:{left}%")
            if top is not None:
                style_parts.append(f"top:{top}%")
            if w is not None and w > 0:
                style_parts.append(f"width:{w}%")
            elif el_type in ("shape", "shape_rect"):
                style_parts.append("width:80%")
            if h is not None and h > 0:
                style_parts.append(f"height:{h}%")
            elif el_type == "shape":
                style_parts.append("min-height:1.2em")
            elif el_type == "shape_rect":
                style_parts.append("min-height:10%")
            if style_parts:
                style_parts.extend(["position:absolute", "margin:0", "box-sizing:border-box", f"z-index:{i}"])
        fill = el.get("fill")
        if fill:
            style_parts.append(f"background-color:{fill}")
        style_str = (" style=\"" + ";".join(style_parts) + "\"") if style_parts else ""

        if el_type == "shape" and "text" in el:
            text = (el["text"] or "").strip()
            if text:
                css_cls = "slide-element slide-text"
                parts.append(f"<p class=\"{css_cls}\"{style_str}>{html.escape(text)}</p>")
        elif el_type == "shape_rect":
            css_cls = "slide-element slide-rect"
            parts.append(f"<div class=\"{css_cls}\"{style_str}></div>")
        elif el_type == "image":
            url = el.get("contentUrl") or el.get("sourceUrl", "")
            if url:
                img_style = ";".join(style_parts) + ";object-fit:contain;" if style_parts else "max-width:100%;height:auto;"
                parts.append(
                    f'<img src="{html.escape(url)}" alt="" class="slide-element slide-image" style="{img_style}" />'
                )
    if not parts:
        return "<div class='slide slide-canvas'><p class='text-muted-foreground'>（空のスライド）</p></div>"
    wrapper_class = "slide slide-canvas" if has_layout else "slide"
    return "<div class='" + wrapper_class + "'>" + "".join(parts) + "</div>"


def _template_contents_to_pages(contents: Any) -> list[tuple[int, dict[str, Any]]]:
    """
    テンプレートの contents から (page_num, page_contents) のリストを返す。
    contents が { "pages": [ { "pageNum", "elements", "pageObjectId" } ], "presentationId"?, "pageSize"?: { widthPt, heightPt } } 形式でない場合は空リスト。
    presentationId, pageObjectId はハイブリッドレンダリング（getThumbnail + Sync）に使用。
    """
    if not isinstance(contents, dict):
        return []
    pages = contents.get("pages")
    if not isinstance(pages, list):
        return []
    page_size = contents.get("pageSize")
    if not isinstance(page_size, dict):
        page_size = None
    presentation_id = contents.get("presentationId")
    if not isinstance(presentation_id, str):
        presentation_id = None
    result: list[tuple[int, dict[str, Any]]] = []
    for p in pages:
        if not isinstance(p, dict):
            continue
        page_num = p.get("pageNum")
        elements = p.get("elements")
        if page_num is None or not isinstance(elements, list):
            continue
        page_contents: dict[str, Any] = {
            "elements": elements,
            "html": _template_elements_to_html(elements),
        }
        if page_size:
            page_contents["pageSize"] = page_size
        if presentation_id:
            page_contents["presentationId"] = presentation_id
        page_object_id = p.get("pageObjectId")
        if isinstance(page_object_id, str):
            page_contents["pageObjectId"] = page_object_id
        result.append((int(page_num), page_contents))
    return result


class SlideUseCases:
    def __init__(
        self,
        repo: SlideRepository,
        google_slides_exporter: GoogleSlidesExporter | None = None,
        template_repo: TemplateRepository | None = None,
        slides_client=None,
    ):
        self.repo = repo
        self.template_repo = template_repo or TemplateRepository()
        self.service = SlideService()
        self.google_slides_exporter = google_slides_exporter
        self._slides_client = slides_client

    # ── Slide CRUD ────────────────────────────────────

    async def create(
        self, owner_id: str, dto: CreateSlideDTO
    ) -> SlideResponseDTO:
        """新規スライドプロジェクト作成 + version 1 を自動生成。テンプレート指定時はそのページを初期表示用にコピー。"""
        template = None
        if dto.template_id:
            template = await self.template_repo.find_by_id(dto.template_id)
            if not template or template.owner_id != owner_id:
                raise NotFoundException("Template", dto.template_id or "")

        slide = await self.repo.create_slide(
            owner_id=owner_id,
            title=dto.title,
            template_id=dto.template_id,
        )
        version = await self.repo.create_version(
            slide_id=slide.id, version_num=1
        )

        # テンプレートのページはコピーせず、1ページのプレースホルダーのみ追加
        placeholder_html = (
            "<div class='slide'><p class='text-muted-foreground'>新しいスライド。左パネルの + からページを追加してください。</p></div>"
            if dto.template_id
            else "<div class='slide'><p class='text-muted-foreground'>新しいスライド</p></div>"
        )
        await self.repo.create_page(
            slide_version_id=version.id,
            page_num=1,
            contents={"html": placeholder_html, "elements": []},
        )

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
        page = await self.repo.create_page(
            slide_version_id=version_id,
            page_num=dto.page_num,
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

    # ── Preview ───────────────────────────────────────

    async def render_preview(self, slide_id: str, version_num: int) -> str:
        """指定バージョンのスライドをHTMLプレビュー生成"""
        # スライド存在確認
        slide = await self.repo.find_slide_by_id(slide_id)
        if not slide:
            raise NotFoundException(f"Slide {slide_id} not found")

        # バージョン取得
        version = await self.repo.find_version_by_num(slide_id, version_num)
        if not version:
            raise NotFoundException(
                f"Version {version_num} not found for slide {slide_id}"
            )

        # ページ一覧取得
        pages = await self.repo.find_pages_by_version(version.id)
        if not pages:
            # ページがない場合は空のプレゼンテーション
            presentation = SlidePresentation(
                title=slide.title or "Untitled", pages=[]
            )
        else:
            # 各ページのcontentsを統合してSlidePresentation作成
            page_data = []
            for page in sorted(pages, key=lambda p: p.page_num):
                if page.contents:
                    page_data.append(page.contents)

            presentation = SlidePresentation(
                title=slide.title or "Untitled", pages=page_data
            )

        # HTML生成
        renderer = HTMLRenderer()
        return renderer.render_presentation(presentation)

    # ── Export ────────────────────────────────────────

    async def export_to_google_slides(
        self, slide_id: str, version_num: int
    ) -> dict[str, str]:
        """指定バージョンのスライドをGoogle Slidesにエクスポート"""
        if not self.google_slides_exporter:
            raise NotFoundException(
                "Google Slides exporter is not configured"
            )

        # スライド存在確認
        slide = await self.repo.find_slide_by_id(slide_id)
        if not slide:
            raise NotFoundException(f"Slide {slide_id} not found")

        # バージョン取得
        version = await self.repo.find_version_by_num(slide_id, version_num)
        if not version:
            raise NotFoundException(
                f"Version {version_num} not found for slide {slide_id}"
            )

        # ページ一覧取得
        pages = await self.repo.find_pages_by_version(version.id)
        if not pages:
            # ページがない場合は空のプレゼンテーション
            presentation = SlidePresentation(
                title=slide.title or "Untitled", pages=[]
            )
        else:
            # 各ページのcontentsを統合してSlidePresentation作成
            page_data = []
            for page in sorted(pages, key=lambda p: p.page_num):
                if page.contents:
                    page_data.append(page.contents)

            presentation = SlidePresentation(
                title=slide.title or "Untitled", pages=page_data
            )

        # Google Slidesにエクスポート
        result = await self.google_slides_exporter.export_presentation(
            presentation
        )
        return result

    # ── Hybrid Rendering ──────────────────────────────

    async def get_page_thumbnail_url(self, page_id: str) -> str | None:
        """
        ページのサムネイル URL を取得（ハイブリッドレンダリング用）。
        page contents に presentationId と pageObjectId がある場合のみ Google API を呼ぶ。
        """
        page = await self.repo.find_page_by_id(page_id)
        if page is None or not self._slides_client:
            return None
        contents = page.contents
        if not isinstance(contents, dict):
            return None
        presentation_id = contents.get("presentationId")
        page_object_id = contents.get("pageObjectId")
        if not isinstance(presentation_id, str) or not isinstance(
            page_object_id, str
        ):
            return None
        try:
            return self._slides_client.get_slide_thumbnail(
                presentation_id, page_object_id
            ) or None
        except Exception:
            return None

    async def sync_page_edits(
        self, page_id: str, dto: SyncPageEditsDTO
    ) -> bool:
        """
        ページ内のテキスト編集を Google スライドに反映（presentations.batchUpdate）。
        edits: 各 Shape の objectId と新しいテキスト。
        """
        page = await self.repo.find_page_by_id(page_id)
        if page is None or not self._slides_client:
            return False
        contents = page.contents
        if not isinstance(contents, dict):
            return False
        presentation_id = contents.get("presentationId")
        if not isinstance(presentation_id, str):
            return False
        requests: list[dict] = []
        for edit in dto.edits:
            obj_id = edit.object_id
            text = edit.text or ""
            # 1. 既存テキストを全削除
            requests.append(
                {"deleteText": {"objectId": obj_id}}
            )
            # 2. 新しいテキストを先頭に挿入
            if text:
                requests.append(
                    {
                        "insertText": {
                            "objectId": obj_id,
                            "text": text,
                            "insertionIndex": 0,
                        }
                    }
                )
        if not requests:
            return True
        try:
            self._slides_client.batch_update(presentation_id, requests)
            return True
        except Exception:
            return False
