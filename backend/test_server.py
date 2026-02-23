"""
テスト用の簡易バックエンドサーバー
フロントエンドの動作確認用 - 実際のレンダリング機能を使用
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# 実際のレンダリング機能をインポート
from app.infrastructure.rendering.schema import (
    SlidePresentation,
    SlidePage,
    TextElement,
    ImageElement,
    ShapeElement,
    ElementPosition,
    TextStyle,
    BackgroundStyle,
)
from app.infrastructure.rendering.html_renderer import HTMLRenderer

app = FastAPI(title="Slide Turbo Test API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExportRequest(BaseModel):
    version_num: int
    presentation_title: str


# HTMLRenderer インスタンス
renderer = HTMLRenderer()


@app.get("/")
def read_root():
    return {"message": "Slide Turbo Test API", "status": "running"}


@app.get("/api/slides/{slide_id}/preview", response_class=HTMLResponse)
def get_slide_preview(slide_id: str, version_num: int = Query(1)):
    """
    実際のHTMLRendererを使用してプレビューを生成
    """
    # モックプレゼンテーションデータを作成
    presentation = SlidePresentation(
        title=f"テストプレゼンテーション (Slide {slide_id})",
        pages=[
            SlidePage(
                page_num=1,
                layout="title_slide",
                background=BackgroundStyle(
                    color="#667eea",
                ),
                elements=[
                    TextElement(
                        element_id="title_1",
                        type="text",
                        position=ElementPosition(x=100, y=150, width=600, height=100),
                        content=f"🎨 Slide Turbo v{version_num}",
                        style=TextStyle(
                            font_size=48,
                            font_weight="bold",
                            color="#ffffff",
                            align="center",
                        ),
                    ),
                    TextElement(
                        element_id="subtitle_1",
                        type="text",
                        position=ElementPosition(x=100, y=280, width=600, height=60),
                        content="実際のHTMLRendererでレンダリング",
                        style=TextStyle(
                            font_size=24,
                            color="#f0f0f0",
                            align="center",
                        ),
                    ),
                ],
                notes=f"スライドID: {slide_id}, バージョン: {version_num}",
            ),
            SlidePage(
                page_num=2,
                layout="title_content",
                background=BackgroundStyle(color="#ffffff"),
                elements=[
                    TextElement(
                        element_id="title_2",
                        type="text",
                        position=ElementPosition(x=50, y=50, width=700, height=60),
                        content="機能テスト",
                        style=TextStyle(
                            font_size=36,
                            font_weight="bold",
                            color="#333333",
                        ),
                    ),
                    TextElement(
                        element_id="content_2",
                        type="text",
                        position=ElementPosition(x=50, y=150, width=700, height=200),
                        content="✓ HTMLレンダリング機能\n✓ 複数ページ対応\n✓ テキストスタイル\n✓ 背景色設定",
                        style=TextStyle(
                            font_size=20,
                            color="#555555",
                            line_height=1.8,
                        ),
                    ),
                    ShapeElement(
                        element_id="shape_2",
                        type="shape",
                        position=ElementPosition(x=50, y=400, width=200, height=80),
                        shape_type="rectangle",
                        fill_color="#667eea",
                        border_color="#764ba2",
                        border_width=3,
                    ),
                ],
            ),
            SlidePage(
                page_num=3,
                layout="blank",
                background=BackgroundStyle(color="#f8f9fa"),
                elements=[
                    TextElement(
                        element_id="success_3",
                        type="text",
                        position=ElementPosition(x=100, y=200, width=600, height=100),
                        content="バックエンド ✓ フロントエンド ✓",
                        style=TextStyle(
                            font_size=32,
                            font_weight="bold",
                            color="#28a745",
                            align="center",
                        ),
                    ),
                ],
            ),
        ],
        author="Test System",
        version=version_num,
    )
    
    # HTMLRendererでレンダリング
    html_content = renderer.render_presentation(presentation)
    return HTMLResponse(content=html_content)


@app.post("/api/slides/{slide_id}/export/google-slides")
def export_to_google_slides(
    slide_id: str,
    request: ExportRequest,
):
    """
    Google Slidesエクスポートのテストエンドポイント
    実際のエクスポートは行わず、モックレスポンスを返す
    """
    presentation_id = f"test_presentation_{slide_id}_v{request.version_num}"
    
    return JSONResponse(
        content={
            "presentation_id": presentation_id,
            "presentation_url": f"https://docs.google.com/presentation/d/{presentation_id}/preview",
            "edit_url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
        }
    )


@app.get("/health")
def health_check():
    return {"status": "healthy", "api": "test-mode"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
