"""
Template Router — テンプレート管理エンドポイント
"""

from fastapi import APIRouter, Depends, Header

from app.application.template.dto import (
    CreateTemplateDTO,
    ImportFromGoogleSlidesDTO,
    TemplateListItemDTO,
    TemplateResponseDTO,
    UpdateTemplateDTO,
)
from app.application.template.usecases import TemplateUseCases
from app.core.auth import get_current_user
from app.infrastructure.google_slides.client import GoogleSlidesClient
from app.infrastructure.google_slides.parser import GoogleSlidesParser
from app.infrastructure.persistence.template_repository import TemplateRepository

router = APIRouter(prefix="/templates", tags=["templates"])


def _get_usecases() -> TemplateUseCases:
    return TemplateUseCases(
        repo=TemplateRepository(),
        slides_parser=GoogleSlidesParser(GoogleSlidesClient()),
    )


# ── Endpoints ─────────────────────────────────────────


@router.post("", response_model=TemplateResponseDTO, status_code=201)
async def create_template(
    body: CreateTemplateDTO,
    current_user=Depends(get_current_user),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレートを手動登録"""
    return await uc.create(current_user.id, body)


@router.post("/import", response_model=TemplateResponseDTO, status_code=201)
async def import_from_google_slides(
    body: ImportFromGoogleSlidesDTO,
    current_user=Depends(get_current_user),
    google_access_token: str | None = Header(
        default=None, alias="X-Google-Access-Token"
    ),
):
    """Google Slides からテンプレートをインポート"""
    uc = TemplateUseCases(
        repo=TemplateRepository(),
        slides_parser=GoogleSlidesParser(
            GoogleSlidesClient(access_token=google_access_token)
        ),
    )
    return await uc.import_from_google_slides(current_user.id, body)


@router.get("", response_model=list[TemplateListItemDTO])
async def list_templates(
    current_user=Depends(get_current_user),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """自分のテンプレート一覧"""
    return await uc.list_by_owner(current_user.id)


@router.get("/{template_id}", response_model=TemplateResponseDTO)
async def get_template(
    template_id: str,
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレート詳細"""
    return await uc.get_by_id(template_id)


@router.patch("/{template_id}", response_model=TemplateResponseDTO)
async def update_template(
    template_id: str,
    body: UpdateTemplateDTO,
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレート更新"""
    return await uc.update(template_id, body)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレート削除"""
    await uc.delete(template_id)
