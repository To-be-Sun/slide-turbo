"""
JSON → HTML変換レンダラー
Google Slides API生フォーマット（pageElements構造）をHTMLプレビューに変換
"""

import html
from typing import Any


class HTMLRenderer:
    """Google Slides API生フォーマットのスライドをHTMLに変換するレンダラー"""
    
    # PT (points) to PX conversion: 1pt = 1.333px (96 DPI standard)
    PT_TO_PX = 1.333

    def render_presentation(self, title: str, pages: list[dict[str, Any]]) -> str:
        """プレゼンテーション全体のHTML生成
        
        Args:
            title: プレゼンテーションタイトル
            pages: Google Slides API形式のページ配列 [{objectId, pageElements: [...]}]
        """
        pages_html = ""
        for idx, page in enumerate(pages):
            pages_html += self.render_page(page, page_num=idx + 1)

        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(title)}</title>
    <style>{self._get_base_styles()}</style>
</head>
<body>
    <div class="presentation-container">
        <h1 class="presentation-title">{self._escape_html(title)}</h1>
        <div class="slides-container">
            {pages_html}
        </div>
        <div class="navigation-info">
            <p>矢印キー（←/→）でページ移動 | 全ページ数: {len(pages)}</p>
        </div>
    </div>
    <script>{self._get_base_scripts()}</script>
</body>
</html>"""

    def render_page(self, page: dict[str, Any], page_num: int) -> str:
        """単一ページのHTML生成
        
        Args:
            page: Google Slides API形式のページ {objectId, pageElements: [...]}
            page_num: ページ番号（表示用）
        """
        page_elements = page.get("pageElements", [])
        elements_html = ""
        
        for element in page_elements:
            elements_html += self._render_element(element)

        return f"""
        <div class="slide" data-page-num="{page_num}">
            <div class="slide-content">
                {elements_html}
            </div>
        </div>
        """

    def _render_element(self, element: dict[str, Any]) -> str:
        """要素タイプごとに分岐
        
        Google Slides API pageElement形式:
        {
          "objectId": "...",
          "transform": {"translateX": float, "translateY": float},
          "size": {"width": {"magnitude": float, "unit": "PT"}, "height": {...}},
          "shape": {...} OR "image": {...}
        }
        """
        if "image" in element:
            return self._render_image(element)
        elif "shape" in element:
            # TEXT_BOX や RECTANGLE などのshape
            return self._render_shape(element)
        return ""

    def _render_shape(self, element: dict[str, Any]) -> str:
        """Shape要素（TEXT_BOX, RECTANGLEなど）のHTML生成"""
        object_id = element.get("objectId", "")
        position_style = self._get_position_style(element)
        
        shape_data = element.get("shape", {})
        shape_type = shape_data.get("shapeType", "TEXT_BOX")
        text_data = shape_data.get("text", {})
        
        # textElementsから実際のテキストコンテンツを抽出
        text_content = self._extract_text_content(text_data)
        
        return (
            f'<div class="shape-element shape-{shape_type.lower()}" '
            f'id="{object_id}" style="{position_style}">'
            f'{self._escape_html(text_content)}'
            f'</div>\n'
        )

    def _render_image(self, element: dict[str, Any]) -> str:
        """Image要素のHTML生成"""
        object_id = element.get("objectId", "")
        position_style = self._get_position_style(element)
        
        image_data = element.get("image", {})
        content_url = image_data.get("contentUrl", "")
        
        return (
            f'<img class="image-element" '
            f'id="{object_id}" '
            f'src="{content_url}" '
            f'alt="Slide image" '
            f'style="{position_style}" />\n'
        )
    
    def _get_position_style(self, element: dict[str, Any]) -> str:
        """transform + sizeからCSSスタイル文字列を生成"""
        transform = element.get("transform", {})
        size_data = element.get("size", {})
        
        # PTをピクセルに変換
        x_pt = transform.get("translateX", 0)
        y_pt = transform.get("translateY", 0)
        width_pt = size_data.get("width", {}).get("magnitude", 100)
        height_pt = size_data.get("height", {}).get("magnitude", 50)
        
        x_px = x_pt * self.PT_TO_PX
        y_px = y_pt * self.PT_TO_PX
        width_px = width_pt * self.PT_TO_PX
        height_px = height_pt * self.PT_TO_PX
        
        return (
            f"position: absolute; "
            f"left: {x_px}px; "
            f"top: {y_px}px; "
            f"width: {width_px}px; "
            f"height: {height_px}px;"
        )
    
    def _extract_text_content(self, text_data: dict[str, Any]) -> str:
        """textElements配列からテキストコンテンツを抽出
        
        Google Slides API text構造:
        {
          "textElements": [
            {"textRun": {"content": "Hello"}},
            {"paragraphMarker": {...}},
            ...
          ]
        }
        """
        text_elements = text_data.get("textElements", [])
        content_parts = []
        
        for elem in text_elements:
            if "textRun" in elem:
                content = elem["textRun"].get("content", "")
                content_parts.append(content)
        
        return "".join(content_parts)

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTMLエスケープ処理"""
        return html.escape(text)

    @staticmethod
    def _get_base_styles() -> str:
        """基本CSSスタイル"""
        return """
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .presentation-container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .presentation-title {
                font-size: 2rem;
                margin-bottom: 30px;
                color: #333;
                text-align: center;
            }
            .slides-container {
                display: flex;
                flex-direction: column;
                gap: 30px;
            }
            .slide {
                position: relative;
                width: 100%;
                aspect-ratio: 16 / 9;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .slide:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .slide-content {
                position: relative;
                width: 100%;
                height: 100%;
            }
            .slide-notes {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px;
                font-size: 0.9rem;
                max-height: 25%;
                overflow-y: auto;
            }
            .text-element {
                overflow-wrap: break-word;
                word-wrap: break-word;
            }
            .image-element {
                object-fit: contain;
            }
            .table-element {
                border-collapse: collapse;
            }
            .table-element td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            .navigation-info {
                margin-top: 20px;
                text-align: center;
                color: #666;
                font-size: 0.9rem;
            }
            @media (max-width: 768px) {
                .slide {
                    aspect-ratio: 4 / 3;
                }
                .presentation-title {
                    font-size: 1.5rem;
                }
            }
        """

    @staticmethod
    def _get_base_scripts() -> str:
        """基本JavaScript（キーボードナビゲーション）"""
        return """
            // キーボードナビゲーション
            let currentSlide = 0;
            const slides = document.querySelectorAll('.slide');
            
            function scrollToSlide(index) {
                if (index >= 0 && index < slides.length) {
                    slides[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    currentSlide = index;
                }
            }
            
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') {
                    scrollToSlide(currentSlide - 1);
                } else if (e.key === 'ArrowRight') {
                    scrollToSlide(currentSlide + 1);
                }
            });
        """
