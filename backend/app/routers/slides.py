from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.types import GenerateSlideRequest, FillSlotRequest, FilledSlot
from app.services.db.template_service import get_template
from app.services.template_to_html import generate_html_from_template
from app.services.slide_renderer import render_slides_from_html, render_single_slide
from app.services.slot_replacer import fill_slot_with_ai, replace_slot_in_html

router = APIRouter(prefix="/api/slides", tags=["slides"])


@router.post("/generate")
async def generate_slides(
    request: GenerateSlideRequest,
    db: Session = Depends(get_db),
):
    """テンプレートとスロットからスライドを生成"""
    try:
        # データベースからテンプレートを取得
        template = get_template(db, request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # HTML生成
        html = await generate_html_from_template(template, request.slots, request.story)
        
        # スライドを画像として描画
        slides = await render_slides_from_html(html)
        
        return {
            "success": True,
            "data": {
                "html": html,
                "slides": [slide.dict() for slide in slides],
            },
        }
    except Exception as e:
        print(f"Error generating slides: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate slides: {str(e)}",
        )


@router.post("/fill-slot")
async def fill_slot(request: FillSlotRequest):
    """AIを使ってスロットを埋める"""
    try:
        if not request.slot_id or request.value is None:
            raise HTTPException(
                status_code=400,
                detail="slotId and value are required",
            )
        
        # AIでスロットを埋める
        filled_value = await fill_slot_with_ai(request)
        
        # HTMLを生成（簡易実装）
        html = f'<div data-slot-id="{request.slot_id}">{filled_value}</div>'
        
        return {
            "success": True,
            "data": {
                "value": filled_value,
                "html": html,
            },
        }
    except Exception as e:
        print(f"Error filling slot: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fill slot: {str(e)}",
        )


class ReplaceSlotRequest(BaseModel):
    html: str
    slot_id: str
    value: str
    slot_type: str


@router.post("/replace-slot")
async def replace_slot(request: ReplaceSlotRequest):
    """HTML内のスロットを置き換え"""
    try:
        if not request.html or not request.slot_id or not request.value or not request.slot_type:
            raise HTTPException(
                status_code=400,
                detail="html, slotId, value, and slotType are required",
            )
        
        updated_html = replace_slot_in_html(
            request.html,
            request.slot_id,
            request.value,
            request.slot_type,
        )
        
        return {
            "success": True,
            "data": {
                "html": updated_html,
            },
        }
    except Exception as e:
        print(f"Error replacing slot: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to replace slot: {str(e)}",
        )


@router.get("/render/{slide_index}")
async def render_slide(
    slide_index: int,
    html: str = Query(..., description="HTML content"),
):
    """特定のスライドを画像としてレンダリング"""
    try:
        image_base64 = await render_single_slide(html, slide_index)
        
        from fastapi.responses import Response
        import base64
        
        image_bytes = base64.b64decode(image_base64)
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        print(f"Error rendering slide: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render slide: {str(e)}",
        )

