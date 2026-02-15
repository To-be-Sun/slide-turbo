"""
Outline (骨子) Router — 骨子管理エンドポイント
"""

from fastapi import APIRouter, Depends

from app.application.outline.dto import (
    CreateOutlineDTO,
    GenerateSlideFromOutlineDTO,
    OutlineResponseDTO,
    RefineOutlineDTO,
    SlideOutputResponseDTO,
    UpdateOutlineDTO,
)
from app.application.outline.usecases import OutlineUseCases
from app.core.auth import get_current_user
from app.infrastructure.persistence.outline_repository import OutlineRepository

router = APIRouter(prefix="/outlines", tags=["outlines"])


def _get_usecases() -> OutlineUseCases:
    return OutlineUseCases(repo=OutlineRepository())


# ── Endpoints ─────────────────────────────────────────


@router.post("", response_model=OutlineResponseDTO, status_code=201)
async def create_outline(
    body: CreateOutlineDTO,
    current_user=Depends(get_current_user),
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """骨子を新規作成"""
    return await uc.create(body)


@router.get(
    "/by-version/{slide_version_id}",
    response_model=list[OutlineResponseDTO],
)
async def list_outlines_by_version(
    slide_version_id: str,
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """バージョンに紐づく骨子一覧"""
    return await uc.list_by_version(slide_version_id)


@router.get("/{outline_id}", response_model=OutlineResponseDTO)
async def get_outline(
    outline_id: str,
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """骨子詳細"""
    return await uc.get_by_id(outline_id)


@router.patch("/{outline_id}", response_model=OutlineResponseDTO)
async def update_outline(
    outline_id: str,
    body: UpdateOutlineDTO,
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """骨子更新"""
    return await uc.update(outline_id, body)


@router.delete("/{outline_id}", status_code=204)
async def delete_outline(
    outline_id: str,
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """骨子削除"""
    await uc.delete(outline_id)


@router.post("/refine", response_model=OutlineResponseDTO)
async def refine_outline(
    body: RefineOutlineDTO,
    current_user=Depends(get_current_user),
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """マルチエージェントで骨子をブラッシュアップ"""
    return await uc.refine(body)


@router.post("/generate-slide", response_model=SlideOutputResponseDTO)
async def generate_slide_from_outline(
    body: GenerateSlideFromOutlineDTO,
    current_user=Depends(get_current_user),
    uc: OutlineUseCases = Depends(_get_usecases),
):
    """骨子から1枚スライドJSONを multi-agent 生成"""
    return await uc.generate_slide(body)
