"""
Google Slides エクスポーター
生成したスライドを Google Slides に書き出し、PPTX ダウンロード URL を返す。
"""

from __future__ import annotations

import re
from typing import Any, Union

from app.infrastructure.google_slides.client import GoogleSlidesClient
from app.infrastructure.rendering.schema import (
    SlidePresentation,
    SlidePage,
    TextElement,
    ImageElement,
    ShapeElement,
    TableElement,
)


class GoogleSlidesExporter:
    """Google Slides 経由で PPTX を出力"""

    def __init__(self, client: GoogleSlidesClient) -> None:
        self.client = client

    async def export_presentation(
        self, presentation: SlidePresentation
    ) -> dict[str, str]:
        """
        SlidePresentation から Google Slides を新規作成し、URL を返す。

        Args:
            presentation: レンダリング用のプレゼンテーションデータ

        Returns:
            {
                "presentation_id": str,
                "presentation_url": str,
                "download_url": str
            }
        """
        # 空のプレゼンテーション作成
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

        # URL生成
        presentation_url = (
            f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        )
        download_url = (
            f"https://docs.google.com/presentation/d/{presentation_id}/export/pptx"
        )

        return {
            "presentation_id": presentation_id,
            "presentation_url": presentation_url,
            "download_url": download_url,
        }

    async def export_to_pptx(
        self,
        title: str,
        pages: list[dict[str, Any]],
    ) -> dict[str, str]:
        """
        レガシーメソッド - 後方互換性のため残す

        TODO: Google Slides API の batchUpdate でスライド構築

        Returns:
            {"presentation_id": str, "download_url": str}
        """
        raise NotImplementedError(
            "Google Slides export is not yet implemented. "
            "Use export_presentation() instead."
        )

    def _build_slide_requests(
        self, page: SlidePage, slide_id: str
    ) -> list[dict[str, Any]]:
        """
        ページから Google Slides リクエストを生成

        Args:
            page: スライドページデータ
            slide_id: スライドID

        Returns:
            リクエストのリスト
        """
        requests = []

        # スライド作成
        requests.append(
            {
                "createSlide": {
                    "objectId": slide_id,
                    "slideLayoutReference": {
                        "predefinedLayout": self._map_layout(page.layout)
                    },
                }
            }
        )

        # 背景設定
        if page.background.color or page.background.image_url:
            bg_requests = self._build_background_requests(
                slide_id, page.background
            )
            requests.extend(bg_requests)

        # 要素追加
        for element in page.elements:
            element_requests = self._build_element_requests(
                element, slide_id
            )
            requests.extend(element_requests)

        return requests

    def _build_background_requests(
        self, slide_id: str, background: Any
    ) -> list[dict[str, Any]]:
        """背景設定リクエスト生成"""
        requests = []

        if background.color:
            rgb = self._hex_to_rgb(background.color)
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

        # 画像背景は未実装（TODOコメント）
        # if background.image_url:
        #     # TODO: createImage で背景画像を追加

        return requests

    def _build_element_requests(
        self,
        element: Union[TextElement, ImageElement, ShapeElement, TableElement],
        slide_id: str,
    ) -> list[dict[str, Any]]:
        """
        要素から Google Slides リクエストを生成

        Args:
            element: スライド要素
            slide_id: スライドID

        Returns:
            リクエストのリスト
        """
        if isinstance(element, TextElement):
            return self._build_text_requests(element, slide_id)
        elif isinstance(element, ImageElement):
            return self._build_image_requests(element, slide_id)
        elif isinstance(element, ShapeElement):
            return self._build_shape_requests(element, slide_id)
        elif isinstance(element, TableElement):
            return self._build_table_requests(element, slide_id)
        else:
            # ChartElement などは未実装
            return []

    def _build_text_requests(
        self, element: TextElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """テキスト要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"
        pos = element.position

        requests = []

        # テキストボックス作成
        requests.append(
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": self._px_to_pt(pos.width), "unit": "PT"},
                            "height": {"magnitude": self._px_to_pt(pos.height), "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self._px_to_pt(pos.x),
                            "translateY": self._px_to_pt(pos.y),
                            "unit": "PT",
                        },
                    },
                }
            }
        )

        # テキスト挿入
        requests.append(
            {
                "insertText": {
                    "objectId": element_id,
                    "text": element.content,
                }
            }
        )

        # テキストスタイル適用
        style = element.style
        rgb = self._hex_to_rgb(style.color)
        requests.append(
            {
                "updateTextStyle": {
                    "objectId": element_id,
                    "fields": "foregroundColor,fontFamily,fontSize,bold",
                    "style": {
                        "foregroundColor": {"opaqueColor": {"rgbColor": rgb}},
                        "fontFamily": style.font_family,
                        "fontSize": {"magnitude": style.font_size, "unit": "PT"},
                        "bold": style.font_weight == "bold",
                    },
                    "textRange": {"type": "ALL"},
                }
            }
        )

        # テキスト配置
        align_map = {"left": "START", "center": "CENTER", "right": "END"}
        requests.append(
            {
                "updateParagraphStyle": {
                    "objectId": element_id,
                    "fields": "alignment",
                    "style": {"alignment": align_map.get(style.align, "START")},
                    "textRange": {"type": "ALL"},
                }
            }
        )

        return requests

    def _build_image_requests(
        self, element: ImageElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """画像要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"
        pos = element.position

        return [
            {
                "createImage": {
                    "objectId": element_id,
                    "url": element.source_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": self._px_to_pt(pos.width), "unit": "PT"},
                            "height": {"magnitude": self._px_to_pt(pos.height), "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self._px_to_pt(pos.x),
                            "translateY": self._px_to_pt(pos.y),
                            "unit": "PT",
                        },
                    },
                }
            }
        ]

    def _build_shape_requests(
        self, element: ShapeElement, slide_id: str
    ) -> list[dict[str, Any]]:
        """図形要素のリクエスト生成"""
        element_id = f"{slide_id}_{element.element_id}"
        pos = element.position

        requests = []

        # 図形作成
        requests.append(
            {
                "createShape": {
                    "objectId": element_id,
                    "shapeType": self._map_shape_type(element.shape_type),
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": self._px_to_pt(pos.width), "unit": "PT"},
                            "height": {"magnitude": self._px_to_pt(pos.height), "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self._px_to_pt(pos.x),
                            "translateY": self._px_to_pt(pos.y),
                            "unit": "PT",
                        },
                    },
                }
            }
        )

        # 塗りつぶし色設定
        fill_rgb = self._hex_to_rgb(element.fill_color)
        requests.append(
            {
                "updateShapeProperties": {
                    "objectId": element_id,
                    "fields": "shapeBackgroundFill.solidFill.color",
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": fill_rgb}}
                        }
                    },
                }
            }
        )

        # 枠線設定
        if element.border_color and element.border_width > 0:
            border_rgb = self._hex_to_rgb(element.border_color)
            requests.append(
                {
                    "updateShapeProperties": {
                        "objectId": element_id,
                        "fields": "outline",
                        "shapeProperties": {
                            "outline": {
                                "outlineFill": {
                                    "solidFill": {"color": {"rgbColor": border_rgb}}
                                },
                                "weight": {
                                    "magnitude": element.border_width,
                                    "unit": "PT",
                                },
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
        pos = element.position

        # テーブル作成（セルテキストは未実装）
        return [
            {
                "createTable": {
                    "objectId": element_id,
                    "rows": element.rows,
                    "columns": element.cols,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": self._px_to_pt(pos.width), "unit": "PT"},
                            "height": {"magnitude": self._px_to_pt(pos.height), "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self._px_to_pt(pos.x),
                            "translateY": self._px_to_pt(pos.y),
                            "unit": "PT",
                        },
                    },
                }
            }
            # TODO: insertText でセル内容を追加
        ]

    @staticmethod
    def _map_layout(layout: str) -> str:
        """レイアウト名をGoogle Slides形式にマッピング"""
        layout_map = {
            "title_slide": "TITLE",
            "title_content": "TITLE_AND_BODY",
            "two_column": "TITLE_AND_TWO_COLUMNS",
            "blank": "BLANK",
            "image_full": "BLANK",  # 画像フルはBLANKとして扱う
        }
        return layout_map.get(layout, "BLANK")

    @staticmethod
    def _map_shape_type(shape_type: str) -> str:
        """図形タイプをGoogle Slides形式にマッピング"""
        shape_map = {
            "rectangle": "RECTANGLE",
            "circle": "ELLIPSE",
            "triangle": "TRIANGLE",
        }
        return shape_map.get(shape_type, "RECTANGLE")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> dict[str, float]:
        """
        HEX色をRGB形式に変換 (0.0-1.0)

        Args:
            hex_color: #RRGGBB 形式

        Returns:
            {"red": float, "green": float, "blue": float}
        """
        # #を除去
        hex_color = hex_color.lstrip("#")

        # RGB値を抽出 (0-255)
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        elif len(hex_color) == 3:
            # 短縮形 (#RGB → #RRGGBB)
            r = int(hex_color[0] * 2, 16)
            g = int(hex_color[1] * 2, 16)
            b = int(hex_color[2] * 2, 16)
        else:
            # デフォルト黒
            return {"red": 0.0, "green": 0.0, "blue": 0.0}

        # 0.0-1.0に正規化
        return {
            "red": r / 255.0,
            "green": g / 255.0,
            "blue": b / 255.0,
        }

    @staticmethod
    def _px_to_pt(px: float) -> float:
        """
        ピクセルをポイント (PT) に変換

        Google Slides APIはPT単位を使用
        1 px ≈ 0.75 pt

        Args:
            px: ピクセル値

        Returns:
            ポイント値
        """
        return px * 0.75
