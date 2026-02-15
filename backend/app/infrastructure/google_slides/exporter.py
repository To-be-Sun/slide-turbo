"""
Google Slides エクスポーター
Google Slides API生フォーマットのスライドをGoogle Slidesに書き出す。
"""

from __future__ import annotations

from typing import Any

from app.infrastructure.google_slides.client import GoogleSlidesClient


class GoogleSlidesExporter:
    """Google Slides API形式のスライドをGoogle Slidesにエクスポート"""

    def __init__(self, client: GoogleSlidesClient | None = None) -> None:
        self.client = client or GoogleSlidesClient()

    async def create_presentation(
        self,
        title: str,
        pages: list[dict[str, Any]],
        owner_email: str | None = None,
    ) -> str:
        """Google Slidesプレゼンテーション作成
        
        Args:
            title: プレゼンテーションタイトル
            pages: Google Slides API形式のページ配列 [{objectId, pageElements: [...]}]
            owner_email: 共有先メールアドレス（オプション）
        
        Returns:
            作成されたプレゼンテーションID
        """
        slides_service = self.client.get_slides_service()
        
        # 1. プレゼンテーション作成
        body = {"title": title}
        created = slides_service.presentations().create(body=body).execute()
        presentation_id = created["presentationId"]

        # 2. 初期スライドを削除して空にする
        initial_slide_id = created["slides"][0]["objectId"]
        requests: list[dict[str, Any]] = [
            {"deleteObject": {"objectId": initial_slide_id}}
        ]

        # 3. 各ページを追加
        for idx, page in enumerate(pages):
            slide_id = page.get("objectId", f"slide_{idx + 1}")
            page_elements = page.get("pageElements", [])
            
            # スライド作成リクエスト
            requests.append(
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "slideLayoutReference": {"predefinedLayout": "BLANK"},
                    }
                }
            )
            
            # 各要素を追加（Google Slides API形式をそのまま使用）
            for element in page_elements:
                if "shape" in element:
                    create_request = self._build_create_shape_request(element, slide_id)
                    requests.append({"createShape": create_request})
                    
                    # テキスト挿入（shape.textがある場合）
                    shape_data = element.get("shape", {})
                    text_data = shape_data.get("text", {})
                    if text_data:
                        text_content = self._extract_text_content(text_data)
                        if text_content:
                            requests.append({
                                "insertText": {
                                    "objectId": element.get("objectId"),
                                    "text": text_content,
                                }
                            })
                elif "image" in element:
                    create_request = self._build_create_image_request(element, slide_id)
                    requests.append({"createImage": create_request})

        # 4. バッチ更新実行
        if requests:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests}
            ).execute()
        
        # 5. （オプション）共有設定
        if owner_email:
            drive_service = self.client.get_drive_service()
            drive_service.permissions().create(
                fileId=presentation_id,
                body={
                    "type": "user",
                    "role": "writer",
                    "emailAddress": owner_email,
                },
            ).execute()

        return presentation_id

    def _build_create_shape_request(
        self, element: dict[str, Any], slide_id: str
    ) -> dict[str, Any]:
        """createShapeリクエスト生成
        
        Google Slides API pageElement形式からcreateShapeリクエストを生成
        """
        object_id = element.get("objectId")
        transform = element.get("transform", {})
        size = element.get("size", {})
        shape_data = element.get("shape", {})
        
        request: dict[str, Any] = {
            "objectId": object_id,
            "shapeType": shape_data.get("shapeType", "TEXT_BOX"),
            "elementProperties": {
                "pageObjectId": slide_id,
                "transform": {
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                    "translateX": transform.get("translateX", 0),
                    "translateY": transform.get("translateY", 0),
                    "unit": "PT",
                },
                "size": {
                    "width": {
                        "magnitude": size.get("width", {}).get("magnitude", 100),
                        "unit": "PT",
                    },
                    "height": {
                        "magnitude": size.get("height", {}).get("magnitude", 50),
                        "unit": "PT",
                    },
                },
            },
        }
        
        return request

    def _build_create_image_request(
        self, element: dict[str, Any], slide_id: str
    ) -> dict[str, Any]:
        """createImageリクエスト生成"""
        object_id = element.get("objectId")
        transform = element.get("transform", {})
        size = element.get("size", {})
        image_data = element.get("image", {})
        
        request: dict[str, Any] = {
            "objectId": object_id,
            "url": image_data.get("contentUrl", ""),
            "elementProperties": {
                "pageObjectId": slide_id,
                "transform": {
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                    "translateX": transform.get("translateX", 0),
                    "translateY": transform.get("translateY", 0),
                    "unit": "PT",
                },
                "size": {
                    "width": {
                        "magnitude": size.get("width", {}).get("magnitude", 100),
                        "unit": "PT",
                    },
                    "height": {
                        "magnitude": size.get("height", {}).get("magnitude", 50),
                        "unit": "PT",
                    },
                },
            },
        }
        
        return request
    
    def _extract_text_content(self, text_data: dict[str, Any]) -> str:
        """textElements配列からテキストコンテンツを抽出"""
        text_elements = text_data.get("textElements", [])
        content_parts = []
        
        for elem in text_elements:
            if "textRun" in elem:
                content = elem["textRun"].get("content", "")
                content_parts.append(content)
        
        return "".join(content_parts)
