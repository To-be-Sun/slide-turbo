"""
Template Router — テンプレート管理エンドポイント
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Header

logger = logging.getLogger(__name__)

from app.application.template.dto import (
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
        slides_client=GoogleSlidesClient(),
    )


# ── Endpoints ─────────────────────────────────────────


@router.post("/import", response_model=TemplateResponseDTO, status_code=201)
async def import_from_google_slides(
    body: ImportFromGoogleSlidesDTO,
    current_user=Depends(get_current_user),
    google_access_token: str | None = Header(
        default=None, alias="X-Google-Access-Token"
    ),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """Google Slides からテンプレートをインポート"""
    logger.info(
        "template import requested: user_id=%s url=%s",
        current_user.id,
        body.presentation_url,
    )
    try:
        result = await uc.import_from_google_slides(current_user.id, body)
    except Exception as e:
        logger.exception("template import failed: %s", e)
        err_msg = str(e).strip() or "不明なエラー"
        if len(err_msg) > 200:
            err_msg = err_msg[:200] + "..."
        detail = (
            "Google Slides の取得に失敗しました。"
            " .env の GOOGLE_REFRESH_TOKEN が正しく、対象スライドにアクセスできるアカウントのトークンか確認してください。"
            f"（詳細: {err_msg}）"
        )
        raise HTTPException(status_code=503, detail=detail) from e
    logger.info(
        "template import completed: template_id=%s title=%s",
        result.id,
        result.title,
    )
    return result


@router.post("/parse-debug")
async def debug_parse(
    body: ImportFromGoogleSlidesDTO,
    current_user=Depends(get_current_user),
):
    """
    デバッグ用: URL をパースし、1ページ目の raw API と計算値を返す。
    配置ずれの診断に使用。本番では無効化を推奨。
    """
    parser = GoogleSlidesParser(GoogleSlidesClient())
    try:
        result = await parser.parse_debug(body.presentation_url)
        return result
    except Exception as e:
        logger.exception("parse-debug failed: %s", e)
        raise HTTPException(status_code=503, detail=str(e)[:500]) from e


@router.post("/import-preview")
async def import_preview(
    body: ImportFromGoogleSlidesDTO,
    current_user=Depends(get_current_user),
):
    """
    インポートプレビュー: URL をパース＋LLM解読し、取得される情報を返す（DBには保存しない）。
    実際にインポートして得られる contents を確認したいときに使用。
    """
    import asyncio
    import json

    parser = GoogleSlidesParser(GoogleSlidesClient())
    try:
        parsed = await parser.parse(body.presentation_url)
    except Exception as e:
        logger.exception("import-preview parse failed: %s", e)
        raise HTTPException(status_code=503, detail=str(e)[:500]) from e

    title = str(parsed.get("title") or "Untitled")
    contents = json.loads(json.dumps(parsed.get("contents") or {}, default=str))

    try:
        from app.infrastructure.ai.template_interpreter import interpret_template
        slots = await asyncio.to_thread(interpret_template, contents)
        if slots:
            contents["slots"] = slots
    except Exception as e:
        logger.warning("import-preview LLM skipped: %s", e)
        contents["slots"] = []

    return {"title": title, "contents": contents}
>>>>>>> pr-9


@router.get("", response_model=list[TemplateListItemDTO])
async def list_templates(
    current_user=Depends(get_current_user),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """自分のテンプレート一覧"""
    return await uc.list_by_owner(current_user.id)


@router.get("/{template_id}/thumbnail")
async def get_template_thumbnail(
    template_id: str,
    current_user=Depends(get_current_user),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレート 1 ページ目のサムネイル URL（Google Slides インポートのみ）。"""
    url = await uc.get_thumbnail_url(template_id)
    if not url:
        raise HTTPException(status_code=404, detail="Thumbnail not available")
    return {"url": url}


@router.get("/{template_id}/thumbnails")
async def get_template_thumbnails(
    template_id: str,
    current_user=Depends(get_current_user),
    uc: TemplateUseCases = Depends(_get_usecases),
):
    """テンプレート全ページのサムネイル URL（Google Slides インポートのみ）。"""
    urls = await uc.get_all_thumbnail_urls(template_id)
    return {"urls": urls}


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
