"""
JSON → HTML変換レンダラー
スライドプレゼンテーションをHTMLプレビューに変換
"""

import html
from typing import Union
from app.infrastructure.rendering.schema import (
    SlidePresentation,
    SlidePage,
    TextElement,
    ImageElement,
    ShapeElement,
    ChartElement,
    TableElement,
    BackgroundStyle,
)


class HTMLRenderer:
    """スライドプレゼンテーションをHTMLに変換するレンダラー"""

    def render_presentation(self, presentation: SlidePresentation) -> str:
        """プレゼンテーション全体のHTML生成"""
        pages_html = ""
        for page in presentation.pages:
            pages_html += self.render_page(page)

        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(presentation.title)}</title>
    <style>{self._get_base_styles()}</style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="presentation-container">
        <h1 class="presentation-title">{self._escape_html(presentation.title)}</h1>
        <div class="slides-container">
            {pages_html}
        </div>
        <div class="navigation-info">
            <p>矢印キー（←/→）でページ移動 | 全ページ数: {len(presentation.pages)}</p>
        </div>
    </div>
    <script>{self._get_base_scripts()}</script>
</body>
</html>"""

    def render_page(self, page: SlidePage) -> str:
        """単一ページのHTML生成"""
        background_style = self._render_background(page.background)
        elements_html = ""
        
        for element in page.elements:
            elements_html += self._render_element(element)

        notes_html = ""
        if page.notes:
            notes_html = f'<div class="slide-notes">{self._escape_html(page.notes)}</div>'

        return f"""
        <div class="slide" data-page-num="{page.page_num}" style="{background_style}">
            <div class="slide-content" data-layout="{page.layout}">
                {elements_html}
            </div>
            {notes_html}
        </div>
        """

    def _render_element(
        self, element: Union[TextElement, ImageElement, ShapeElement, ChartElement, TableElement]
    ) -> str:
        """要素タイプごとに分岐"""
        if isinstance(element, TextElement):
            return self._render_text(element)
        elif isinstance(element, ImageElement):
            return self._render_image(element)
        elif isinstance(element, ShapeElement):
            return self._render_shape(element)
        elif isinstance(element, ChartElement):
            return self._render_chart(element)
        elif isinstance(element, TableElement):
            return self._render_table(element)
        return ""

    def _render_text(self, element: TextElement) -> str:
        """テキスト要素のHTML生成"""
        style = element.style
        inline_style = (
            f"position: absolute; "
            f"left: {element.position.x}px; "
            f"top: {element.position.y}px; "
            f"width: {element.position.width}px; "
            f"height: {element.position.height}px; "
            f"font-family: {style.font_family}; "
            f"font-size: {style.font_size}px; "
            f"font-weight: {style.font_weight}; "
            f"color: {style.color}; "
            f"text-align: {style.align}; "
            f"line-height: {style.line_height}; "
            f"z-index: {element.z_index};"
        )
        
        content = self._escape_html(element.content)
        return f'<div class="text-element" id="{element.element_id}" style="{inline_style}">{content}</div>\n'

    def _render_image(self, element: ImageElement) -> str:
        """画像要素のHTML生成"""
        inline_style = (
            f"position: absolute; "
            f"left: {element.position.x}px; "
            f"top: {element.position.y}px; "
            f"width: {element.position.width}px; "
            f"height: {element.position.height}px; "
            f"z-index: {element.z_index};"
        )
        
        alt_text = self._escape_html(element.alt_text)
        return f'<img class="image-element" id="{element.element_id}" src="{element.source_url}" alt="{alt_text}" style="{inline_style}" />\n'

    def _render_shape(self, element: ShapeElement) -> str:
        """図形要素のHTML生成"""
        border_radius = "50%" if element.shape_type == "circle" else "0"
        border_style = ""
        if element.border_color and element.border_width > 0:
            border_style = f"border: {element.border_width}px solid {element.border_color};"

        inline_style = (
            f"position: absolute; "
            f"left: {element.position.x}px; "
            f"top: {element.position.y}px; "
            f"width: {element.position.width}px; "
            f"height: {element.position.height}px; "
            f"background-color: {element.fill_color}; "
            f"border-radius: {border_radius}; "
            f"{border_style} "
            f"z-index: {element.z_index};"
        )
        
        return f'<div class="shape-element shape-{element.shape_type}" id="{element.element_id}" style="{inline_style}"></div>\n'

    def _render_chart(self, element: ChartElement) -> str:
        """グラフ要素のHTML生成"""
        inline_style = (
            f"position: absolute; "
            f"left: {element.position.x}px; "
            f"top: {element.position.y}px; "
            f"width: {element.position.width}px; "
            f"height: {element.position.height}px; "
            f"z-index: {element.z_index};"
        )
        
        # Chart.js用のdata属性（JSON文字列としてエスケープ）
        import json
        chart_data = html.escape(json.dumps(element.data))
        
        return f'<canvas class="chart-element" id="{element.element_id}" data-chart-type="{element.chart_type}" data-chart-data="{chart_data}" style="{inline_style}"></canvas>\n'

    def _render_table(self, element: TableElement) -> str:
        """表要素のHTML生成"""
        inline_style = (
            f"position: absolute; "
            f"left: {element.position.x}px; "
            f"top: {element.position.y}px; "
            f"width: {element.position.width}px; "
            f"height: {element.position.height}px; "
            f"z-index: {element.z_index};"
        )
        
        rows_html = ""
        for row in element.cells:
            cells_html = "".join([f"<td>{self._escape_html(cell)}</td>" for cell in row])
            rows_html += f"<tr>{cells_html}</tr>"
        
        return f'<table class="table-element" id="{element.element_id}" style="{inline_style}"><tbody>{rows_html}</tbody></table>\n'

    def _render_background(self, background: BackgroundStyle) -> str:
        """背景スタイルのCSS文字列生成"""
        styles = []
        if background.color:
            styles.append(f"background-color: {background.color}")
        if background.image_url:
            styles.append(f"background-image: url('{background.image_url}')")
            styles.append("background-size: cover")
            styles.append("background-position: center")
        return "; ".join(styles) + ";" if styles else ""

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
        """基本JavaScript"""
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
            
            // Chart.js初期化
            document.addEventListener('DOMContentLoaded', () => {
                const chartElements = document.querySelectorAll('.chart-element');
                chartElements.forEach(canvas => {
                    const chartType = canvas.dataset.chartType;
                    const chartData = JSON.parse(canvas.dataset.chartData);
                    new Chart(canvas, {
                        type: chartType,
                        data: chartData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                });
            });
        """
