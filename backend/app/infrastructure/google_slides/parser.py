"""
Google Slides パーサー
プレゼンテーションデータをパースし、テンプレートとして取り込む。
"""

from __future__ import annotations

import re
from typing import Any

from app.infrastructure.google_slides.client import GoogleSlidesClient


class GoogleSlidesParser:
    """Google Slides をパースしてテンプレート構造に変換"""

    def __init__(self, client: GoogleSlidesClient) -> None:
        self.client = client

    @staticmethod
    def extract_presentation_id(url_or_id: str) -> str:
        """URL またはプレゼンテーション ID からIDを抽出"""
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_or_id)
        if match:
            return match.group(1)
        return url_or_id

    async def parse(self, url_or_id: str) -> dict[str, Any]:
        """
        Google Slides をフェッチし、テンプレート構造を返す。

        Returns:
            {"title": str, "contents": dict}
        """
        presentation_id = self.extract_presentation_id(url_or_id)
        presentation = self.client.get_presentation(presentation_id)

        title = presentation.get("title", "Untitled")
        slides = presentation.get("slides", [])

        pages = []
        for i, slide in enumerate(slides):
            pages.append(
                {
                    "pageNum": i + 1,
                    "pageObjectId": slide.get("objectId"),
                    "elements": self._extract_elements(slide),
                }
            )

        return {
            "title": title,
            "contents": {
                "presentationId": presentation_id,
                "pageCount": len(slides),
                "pages": pages,
            },
        }

    @staticmethod
    def _extract_elements(slide: dict) -> list[dict]:
        """スライド内の要素 (テキスト, 画像, 図形) を抽出"""
        elements = []
        for element in slide.get("pageElements", []):
            el: dict[str, Any] = {
                "objectId": element.get("objectId"),
                "type": "unknown",
            }
            if "shape" in element:
                el["type"] = "shape"
                text_content = (
                    element.get("shape", {})
                    .get("text", {})
                    .get("textElements", [])
                )
                el["text"] = " ".join(
                    te.get("textRun", {}).get("content", "")
                    for te in text_content
                    if "textRun" in te
                ).strip()
            elif "image" in element:
                el["type"] = "image"
                el["sourceUrl"] = element["image"].get("sourceUrl", "")
            elements.append(el)
        return elements
