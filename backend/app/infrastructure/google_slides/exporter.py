"""
Google Slides エクスポーター
生成したスライドを Google Slides に書き出し、PPTX ダウンロード URL を返す。
"""

from __future__ import annotations

from typing import Any, Union

from app.infrastructure.google_slides.client import GoogleSlidesClient
from app.infrastructure.rendering.schema import (
    SlidePresentation,
    SlidePage,
    TextElement,
    ImageElement,
    ShapeElement,
    TableElement,
    ElementPosition,
)

# ─────────────────────────────────────────────────────
# 定数定義
# ─────────────────────────────────────────────────────

LAYOUT_MAPPING = {
    "title_slide": "TITLE",
    "title_content": "TITLE_AND_BODY",
    "two_column": "TITLE_AND_TWO_COLUMNS",
    "blank": "BLANK",
    "image_full": "BLANK",
}

SHAPE_TYPE_MAPPING = {
    "rectangle": "RECTANGLE",
    "circle": "ELLIPSE",
    "triangle": "TRIANGLE",
}

TEXT_ALIGN_MAPPING = {
    "left": "START",
    "center": "CENTER",
    "right": "END",
}

# PT変換係数（1 px ≈ 0.75 pt）
PX_TO_PT_RATIO = 0.75


# ─────────────────────────────────────────────────────
# ヘルパー関数
# ─────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> dict[str, float]:
    """HEX色をRGB形式に変換 (0.0-1.0)"""
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    elif len(hex_color) == 3:
        r, g, b = int(hex_color[0] * 2, 16), int(hex_color[1] * 2, 16), int(hex_color[2] * 2, 16)
    else:
        return {"red": 0.0, "green": 0.0, "blue": 0.0}

    return {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}


def px_to_pt(px: float) -> float:
    """ピクセルをポイント (PT) に変換"""
    return px * PX_TO_PT_RATIO


# ─────────────────────────────────────────────────────
# GoogleSlidesExporter
# ─────────────────────────────────────────────────────

class GoogleSlidesExporter:
    """Google Slides 経由で PPTX を出力"""

    def __init__(self, client: GoogleSlidesClient) -> None:
        self.client = client

    async def export_presentation(
        self, presentation: SlidePresentation
    ) -> dict[str, str]:
        """SlidePresentation から Google Slides を作成"""
        slides_service = self.client.get_slides_service()
        body = {"title": presentation.title}
        created = slides_service.presentations().create(body=body).execute()
        presentation_id = created["presentationId"]

        # 初期スライドを削除
        initial_slide_id = created["slides"][0]["objectId"]
        requests = [{"deleteObject": {"objectId": initial_slide_id}}]

        # 各ページのスライド作成リクエストを生成
        for idx, page in enumerate(presentation.pages):
            slide_id = f"slide_{idx + 1}"
            page_requests = self._build_slide_requests(page, slide_id)
            requests.extend(page_requests)

        # バッチ更新実行
        if requests:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests}
            ).execute()

        return {
            "presentation_id": presentation_id,
            "presentation_url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
            "download_url": f"https://docs.google.com/presentation/d/{presentation_id}/export/pptx",
        }

    async def export_to_pptx(
        self, title: str, pages: list[dict[str, Any]]
    ) -> dict[str, str]:
        """レガシーメソッド - 後方互換性のため残す"""
        raise NotImplementedError(
            "Use export_presentation() instead."
        )

    # ─────────────────────────────────────────────────
    # スライド構築
    # ─────────────────────────────────────────────────

    def _build_slide_requests(
        self, page: SlidePage, slide_id: str
    ) -> list[dict[str, Any]]:
        """ページから Google Slides リクエストを生成"""
        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {
                        "predefinedLayout": LAYOUT_MAPPING.get(page.layout, "BLANK")
                    },
                }
            }
        ]

        # 背景設定
        if page.background.color or page.background.image_url:
            requests.extend(self._build_background_requests(slide_id, page.background))

        # 要素追加
        for element in page.elements:
            requests.extend(self._build_element_requests(element, slide_id))

        return requests

    def _build_background_requests(
        self, slide_id: str, background: Any
    ) -> list[dict[str, Any]]:
        """背景設定リクエスト生成"""
        requests = []

        if background.color:
            rgb = hex_to_rgb(background.color)
            requests.append(
                {
                    "updatePageProperties": {
                        "objectId": slide_id,
                        "fields": "pageBackgroundFill.solidFill.color",
                        "pageProperties": {
                            "pageBackgroundFill": {
                                "solidFill": {"color": {"rgbColor": rgb}}
                            }
                        },
                    }
                }
            )

        # TODO: 背景画像対応
        # if background.image_url:
        #     pass

        return requests

    # ─────────────────────────────────────────────────
    # 要素リクエスト生成
    # ─────────────────────────────────────────────────

    def _build_element_requests(
        self,
        element: Union[TextElement, ImageElement, ShapeElement, TableElement],
        slide_id: str,
    ) -> list[dict[str, Any]]:
        """要素タイプごとにリクエストを生成"""
        if isinstance(element, TextElement):
            return self._build_text_requests(element, slide_id)
        elif isinstance(element, ImageElement):
            return self._build_image_requests(element, slide_id)
        elif isinstance(element, ShapeElement):
            return self._build_shape_requests(element, slide_id)
        elif isinstance(element, TableElement):
            return self._build_table_requests(element, slide_id)
        else:
            return []

    def _build_element_properties(
        self, slide_id: str, position: ElementPosition
    ) -> dict[str, Any]:
        """共通の要素プロパティを生成"""
        return {
            "pageObjectId": slide_id,
            "size": {
                "width": {"magnitude": px_to_pt(position.width), "unit": "PT"},
                "height": {"magnitude": px_to_pt(position.height), "unit": "PT"},
            },
            "transform": {
                "scaleX": 1,
                "scaleY": 1,
                "translateX": px_to_pt(position.x),
                "translateY": px_to_pt(position.y),
                "unit": "PT",
            },
        }

    def _build_text_requests(
        self, element: TextElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """テキスト要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"
        style = element.style

        requests = [
            # テキストボックス作成
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": self._build_element_properties(slide_id, element.position),
                }
            },
            # テキスト挿入
            {"insertText": {"objectId": element_id, "text": element.content}},
            # テキストスタイル適用
            {
                "updateTextStyle": {
                    "objectId": element_id,
                    "fields": "foregroundColor,fontFamily,fontSize,bold",
                    "style": {
                        "foregroundColor": {"opaqueColor": {"rgbColor": hex_to_rgb(style.color)}},
                        "fontFamily": style.font_family,
                        "fontSize": {"magnitude": style.font_size, "unit": "PT"},
                        "bold": style.font_weight == "bold",
                    },
                    "textRange": {"type": "ALL"},
                }
            },
            # テキスト配置
            {
                "updateParagraphStyle": {
                    "objectId": element_id,
                    "fields": "alignment",
                    "style": {"alignment": TEXT_ALIGN_MAPPING.get(style.align, "START")},
                    "textRange": {"type": "ALL"},
                }
            },
        ]

        return requests

    def _build_image_requests(
        self, element: ImageElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """画像要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"

        return [
            {
                "createImage": {
                    "objectId": element_id,
                    "url": element.source_url,
                    "elementProperties": self._build_element_properties(slide_id, element.position),
                }
            }
        ]

    def _build_shape_requests(
        self, element: ShapeElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """図形要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"

        requests = [
            # 図形作成
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": SHAPE_TYPE_MAPPING.get(element.shape_type, "RECTANGLE"),
                    "elementProperties": self._build_element_properties(slide_id, element.position),
                }
            },
            # 塗りつぶし色設定
            {
                "updateShapeProperties": {
                    "objectId": element_id,
                    "fields": "shapeBackgroundFill.solidFill.color",
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": hex_to_rgb(element.fill_color)}}
                        }
                    },
                }
            },
        ]

        # 枠線設定（オプション）
        if element.border_color and element.border_width > 0:
            requests.append(
                {
                    "updateShapeProperties": {
                        "objectId": element_id,
                        "fields": "outline",
                        "shapeProperties": {
                            "outline": {
                                "outlineFill": {
                                    "solidFill": {"color": {"rgbColor": hex_to_rgb(element.border_color)}}
                                },
                                "weight": {"magnitude": element.border_width, "unit": "PT"},
                            }
                        },
                    }
                }
            )

        return requests

    def _build_table_requests(
        self, element: TableElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """テーブル要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"

        return [
            {
                "createTable": {
                    "objectId": element_id,
                    "rows": element.rows,
                    "columns": element.cols,
                    "elementProperties": self._build_element_properties(slide_id, element.position),
                }
            }
            # TODO: セル内容の挿入
        ]
