"""
Slide (Project) Router — スライドプロジェクト管理エンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse

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
from app.application.slide.usecases import SlideUseCases
from app.core.auth import get_current_user
from app.infrastructure.google_slides.client import GoogleSlidesClient
from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
from app.infrastructure.persistence.slide_repository import SlideRepository
from app.infrastructure.persistence.template_repository import (
    TemplateRepository,
)

router = APIRouter(prefix="/slides", tags=["slides"])


def _get_usecases() -> SlideUseCases:
    return SlideUseCases(
        repo=SlideRepository(),
        google_slides_exporter=GoogleSlidesExporter(GoogleSlidesClient()),
        template_repo=TemplateRepository(),
        slides_client=GoogleSlidesClient(),
    )


# ── Slide CRUD ────────────────────────────────────────


@router.post("", response_model=SlideResponseDTO, status_code=201)
async def create_slide(
    body: CreateSlideDTO,
    current_user=Depends(get_current_user),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """スライドプロジェクト新規作成"""
    return await uc.create(current_user.id, body)


@router.get("", response_model=list[SlideListItemDTO])
async def list_slides(
    current_user=Depends(get_current_user),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """自分のスライド一覧"""
    return await uc.list_by_owner(current_user.id)


@router.get("/{slide_id}", response_model=SlideResponseDTO)
async def get_slide(
    slide_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """スライド詳細"""
    return await uc.get_by_id(slide_id)


@router.patch("/{slide_id}", response_model=SlideResponseDTO)
async def update_slide(
    slide_id: str,
    body: UpdateSlideDTO,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """スライド更新"""
    return await uc.update(slide_id, body)


@router.delete("/{slide_id}", status_code=204)
async def delete_slide(
    slide_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """スライド削除"""
    await uc.delete(slide_id)


# ── Version ───────────────────────────────────────────


@router.post(
    "/{slide_id}/versions",
    response_model=SlideVersionResponseDTO,
    status_code=201,
)
async def create_version(
    slide_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """新バージョン作成"""
    return await uc.create_version(slide_id)


@router.get(
    "/{slide_id}/versions",
    response_model=list[SlideVersionResponseDTO],
)
async def list_versions(
    slide_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """バージョン一覧"""
    return await uc.list_versions(slide_id)


# ── Page ──────────────────────────────────────────────


@router.post(
    "/versions/{version_id}/pages",
    response_model=PageResponseDTO,
    status_code=201,
)
async def add_page(
    version_id: str,
    body: CreatePageDTO,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """ページ追加"""
    return await uc.add_page(version_id, body)


@router.get(
    "/versions/{version_id}/pages",
    response_model=list[PageResponseDTO],
)
async def list_pages(
    version_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """ページ一覧 (pageNum 昇順)"""
    return await uc.list_pages(version_id)


@router.patch("/pages/{page_id}", response_model=PageResponseDTO)
async def update_page(
    page_id: str,
    body: UpdatePageDTO,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """ページ更新"""
    return await uc.update_page(page_id, body)


# ── Preview ───────────────────────────────────────────


@router.get("/{slide_id}/preview", response_class=HTMLResponse)
async def preview_slide(
    slide_id: str,
    version: int = Query(1, description="プレビューするバージョン番号"),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """スライドHTMLプレビュー生成 (手動リフレッシュ)"""
    html_content = await uc.render_preview(slide_id, version)
    return HTMLResponse(content=html_content)


@router.post("/{slide_id}/export/google-slides")
async def export_to_google_slides(
    slide_id: str,
    version: int = Query(1, description="エクスポートするバージョン番号"),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """Google Slidesエクスポート"""
    result = await uc.export_to_google_slides(slide_id, version)
    return {"success": True, "data": result}


# ── Hybrid Rendering ──────────────────────────────────


@router.get("/pages/{page_id}/thumbnail")
async def get_page_thumbnail(
    page_id: str,
    current_user=Depends(get_current_user),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """
    ページのサムネイル URL 取得（ハイブリッドレンダリング用）。
    presentationId + pageObjectId が page contents にある場合のみ Google API を呼ぶ。
    """
    url = await uc.get_page_thumbnail_url(page_id)
    if url is None:
        raise HTTPException(
            status_code=404,
            detail="Thumbnail not available (page may not be from Google Slides)",
        )
    return {"url": url}


@router.post("/pages/{page_id}/sync")
async def sync_page_edits(
    page_id: str,
    body: SyncPageEditsDTO,
    current_user=Depends(get_current_user),
    uc: SlideUseCases = Depends(_get_usecases),
):
    """
    ページ内のテキスト編集を Google スライドに反映。
    edits: [{ object_id: Shape の objectId, text: 新しいテキスト }]
    """
    ok = await uc.sync_page_edits(page_id, body)
    if not ok:
        raise HTTPException(
            status_code=503,
            detail="Sync failed (check presentationId and Google API credentials)",
        )
    return {"ok": True}
