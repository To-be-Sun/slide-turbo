from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.config.google_slides import get_auth_url, set_auth_token, get_google_slides_client
from app.services.google_slides_parser import fetch_presentation, extract_slide_elements
from app.services.slides_to_html import convert_presentation_to_html, convert_slide_to_html
from app.services.gemini_reviewer import review_presentation, review_slide_html
from app.services.db.template_service import create_template
import re

router = APIRouter(prefix="/api/google-slides", tags=["google-slides"])


class PresentationIdRequest(BaseModel):
    presentation_id: str


class URLRequest(BaseModel):
    url: str


class ReviewSlideRequest(BaseModel):
    html: str
    slide_index: int


@router.get("/auth")
async def get_auth():
    """Google認証URLを取得"""
    try:
        auth_url = get_auth_url()
        return {
            "success": True,
            "data": {
                "authUrl": auth_url,
            },
        }
    except Exception as e:
        print(f"Error generating auth URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate auth URL: {str(e)}",
        )


@router.get("/callback")
async def callback(code: str):
    """OAuthコールバック"""
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        refresh_token = set_auth_token(code)
        
        return {
            "success": True,
            "message": "Authentication successful. Please save the refresh token to your .env file.",
            "refresh_token": refresh_token,
        }
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}",
        )


@router.post("/import")
async def import_presentation(
    request: PresentationIdRequest,
    db: Session = Depends(get_db),
):
    """Google SlidesプレゼンテーションをインポートしてHTMLテンプレートを生成"""
    try:
        # プレゼンテーションを取得
        presentation = fetch_presentation(request.presentation_id)
        
        if not presentation.get("slides"):
            raise HTTPException(status_code=400, detail="No slides found in presentation")
        
        # HTMLに変換
        html = convert_presentation_to_html(presentation)
        
        # 各スライドのHTMLを抽出
        slides_html: list[str] = []
        for i, slide in enumerate(presentation.get("slides", [])):
            elements = extract_slide_elements(slide)
            slide_html = convert_slide_to_html(elements, i)
            slides_html.append(slide_html)
        
        # Geminiでレビュー
        review = await review_presentation(slides_html)
        
        # スロットを生成
        slots = []
        for slide_index, slide_review in enumerate(review.slide_reviews):
            for slot in slide_review.suggested_slots:
                slots.append({
                    "slide_index": slide_index,
                    "name": slot.name,
                    "type": slot.type,
                    "placeholder": slot.placeholder,
                    "required": slot.required,
                })
        
        # テンプレートをDBに保存
        saved_template = create_template(
            db,
            name=review.title,
            description=review.description,
            thumbnail=presentation.get("title", "") or "",
            slide_count=len(presentation.get("slides", [])),
            html=html,
            slots=slots,
        )
        
        return {
            "success": True,
            "data": {
                "template": saved_template.dict(),
                "html": html,
                "review": review.dict(),
            },
        }
    except Exception as e:
        print(f"Error importing Google Slides: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import Google Slides: {str(e)}",
        )


@router.post("/parse-url")
async def parse_url(
    request: URLRequest,
    db: Session = Depends(get_db),
):
    """Google Slides URLからプレゼンテーションIDを抽出してインポート"""
    try:
        # URLからプレゼンテーションIDを抽出
        match = re.search(r"/presentation/d/([a-zA-Z0-9-_]+)", request.url)
        if not match or not match.group(1):
            raise HTTPException(status_code=400, detail="Invalid Google Slides URL")
        
        presentation_id = match.group(1)
        
        # インポート処理を実行
        presentation = fetch_presentation(presentation_id)
        html = convert_presentation_to_html(presentation)
        
        slides_html: list[str] = []
        for i, slide in enumerate(presentation.get("slides", [])):
            elements = extract_slide_elements(slide)
            slide_html = convert_slide_to_html(elements, i)
            slides_html.append(slide_html)
        
        review = await review_presentation(slides_html)
        
        slots = []
        for slide_index, slide_review in enumerate(review.slide_reviews):
            for slot in slide_review.suggested_slots:
                slots.append({
                    "slide_index": slide_index,
                    "name": slot.name,
                    "type": slot.type,
                    "placeholder": slot.placeholder,
                    "required": slot.required,
                })
        
        # テンプレートをDBに保存
        saved_template = create_template(
            db,
            name=review.title,
            description=review.description,
            thumbnail=presentation.get("title", "") or "",
            slide_count=len(presentation.get("slides", [])),
            html=html,
            slots=slots,
        )
        
        return {
            "success": True,
            "data": {
                "presentationId": presentation_id,
                "template": saved_template.dict(),
                "html": html,
                "review": review.dict(),
            },
        }
    except Exception as e:
        print(f"Error parsing Google Slides URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Google Slides URL: {str(e)}",
        )


@router.post("/review-slide")
async def review_slide(request: ReviewSlideRequest):
    """単一スライドのHTMLをレビュー"""
    try:
        review = await review_slide_html(request.html, request.slide_index)
        
        return {
            "success": True,
            "data": review.dict(),
        }
    except Exception as e:
        print(f"Error reviewing slide: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to review slide: {str(e)}",
        )

