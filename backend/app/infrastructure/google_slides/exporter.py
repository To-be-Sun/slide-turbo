"""
Google Slides エクスポーター
生成したスライドを Google Slides に書き出し、PPTX ダウンロード URL を返す。
"""

from __future__ import annotations

from typing import Any

from app.infrastructure.google_slides.client import GoogleSlidesClient


class GoogleSlidesExporter:
    """Google Slides 経由で PPTX を出力"""

    def __init__(self, client: GoogleSlidesClient) -> None:
        self.client = client

    async def export_to_pptx(
        self,
        title: str,
        pages: list[dict[str, Any]],
    ) -> dict[str, str]:
        """
        ページデータから Google Slides を新規作成し、PPTX ダウンロード URL を返す。

        TODO: Google Slides API の batchUpdate でスライド構築

        Returns:
            {"presentation_id": str, "download_url": str}
        """
        raise NotImplementedError(
            "Google Slides export is not yet implemented"
        )
