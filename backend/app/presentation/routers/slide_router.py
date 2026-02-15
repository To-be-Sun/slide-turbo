"""
Slide (Project) Router — スライドプロジェクト管理エンドポイント
"""

from fastapi import APIRouter, Depends

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
from app.application.slide.usecases import SlideUseCases
from app.core.auth import get_current_user
from app.infrastructure.persistence.slide_repository import SlideRepository

router = APIRouter(prefix="/slides", tags=["slides"])


def _get_usecases() -> SlideUseCases:
    return SlideUseCases(repo=SlideRepository())


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


@router.delete("/pages/{page_id}", status_code=204)
async def delete_page(
    page_id: str,
    uc: SlideUseCases = Depends(_get_usecases),
):
    """ページ削除"""
    await uc.delete_page(page_id)
