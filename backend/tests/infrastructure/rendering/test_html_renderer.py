"""
Tests for HTML renderer
"""

import pytest
from app.infrastructure.rendering.html_renderer import HTMLRenderer
from app.infrastructure.rendering.schema import (
    ElementPosition,
    TextStyle,
    BackgroundStyle,
    TextElement,
    ImageElement,
    ShapeElement,
    ChartElement,
    TableElement,
    SlidePage,
    SlidePresentation,
)


class TestHTMLRenderer:
    """HTMLRenderer tests"""

    @pytest.fixture
    def renderer(self):
        """HTMLRendererインスタンス"""
        return HTMLRenderer()

    def test_escape_html(self, renderer):
        """HTMLエスケープ処理"""
        assert renderer._escape_html("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        assert renderer._escape_html("Hello & World") == "Hello &amp; World"
        assert renderer._escape_html('Test "quotes"') == "Test &quot;quotes&quot;"

    def test_render_background_color_only(self, renderer):
        """背景色のみ"""
        bg = BackgroundStyle(color="#FF0000")
        result = renderer._render_background(bg)
        assert "background-color: #FF0000" in result

    def test_render_background_image_only(self, renderer):
        """背景画像のみ"""
        bg = BackgroundStyle(image_url="https://example.com/bg.jpg")
        result = renderer._render_background(bg)
        assert "background-image: url('https://example.com/bg.jpg')" in result
        assert "background-size: cover" in result
        assert "background-position: center" in result

    def test_render_background_both(self, renderer):
        """背景色と画像の両方"""
        bg = BackgroundStyle(color="#FFFFFF", image_url="https://example.com/bg.jpg")
        result = renderer._render_background(bg)
        assert "background-color: #FFFFFF" in result
        assert "background-image:" in result

    def test_render_background_empty(self, renderer):
        """空の背景"""
        bg = BackgroundStyle()
        result = renderer._render_background(bg)
        assert result == ""

    def test_render_text_element(self, renderer):
        """テキスト要素のレンダリング"""
        elem = TextElement(
            element_id="text-1",
            type="text",
            position=ElementPosition(x=100, y=200, width=600, height=100),
            content="Hello World",
            style=TextStyle(font_size=24, color="#FF0000", font_weight="bold"),
        )
        result = renderer._render_text(elem)
        
        assert 'id="text-1"' in result
        assert "Hello World" in result
        assert "left: 100px" in result or "left: 100.0px" in result
        assert "top: 200px" in result or "top: 200.0px" in result
        assert "font-size: 24px" in result or "font-size: 24.0px" in result
        assert "color: #FF0000" in result
        assert "font-weight: bold" in result

    def test_render_text_element_escapes_html(self, renderer):
        """テキスト要素のHTMLエスケープ"""
        elem = TextElement(
            element_id="text-2",
            type="text",
            position=ElementPosition(x=0, y=0, width=100, height=50),
            content="<script>alert('test')</script>",
        )
        result = renderer._render_text(elem)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_render_image_element(self, renderer):
        """画像要素のレンダリング"""
        elem = ImageElement(
            element_id="img-1",
            type="image",
            position=ElementPosition(x=50, y=100, width=400, height=300),
            source_url="https://example.com/image.jpg",
            alt_text="Test Image",
        )
        result = renderer._render_image(elem)
        
        assert 'id="img-1"' in result
        assert 'src="https://example.com/image.jpg"' in result
        assert 'alt="Test Image"' in result
        assert "left: 50px" in result or "left: 50.0px" in result
        assert "width: 400px" in result or "width: 400.0px" in result

    def test_render_shape_rectangle(self, renderer):
        """矩形図形のレンダリング"""
        elem = ShapeElement(
            element_id="shape-1",
            type="shape",
            position=ElementPosition(x=100, y=100, width=200, height=150),
            shape_type="rectangle",
            fill_color="#CCCCCC",
        )
        result = renderer._render_shape(elem)
        
        assert 'id="shape-1"' in result
        assert "background-color: #CCCCCC" in result
        assert "border-radius: 0" in result

    def test_render_shape_circle(self, renderer):
        """円形図形のレンダリング"""
        elem = ShapeElement(
            element_id="shape-2",
            type="shape",
            position=ElementPosition(x=100, y=100, width=150, height=150),
            shape_type="circle",
            fill_color="#FF0000",
        )
        result = renderer._render_shape(elem)
        
        assert 'id="shape-2"' in result
        assert "background-color: #FF0000" in result
        assert "border-radius: 50%" in result

    def test_render_shape_with_border(self, renderer):
        """ボーダー付き図形のレンダリング"""
        elem = ShapeElement(
            element_id="shape-3",
            type="shape",
            position=ElementPosition(x=0, y=0, width=100, height=100),
            shape_type="rectangle",
            fill_color="#FFFFFF",
            border_color="#000000",
            border_width=2.0,
        )
        result = renderer._render_shape(elem)
        
        assert "border: 2" in result
        assert "solid #000000" in result

    def test_render_chart_element(self, renderer):
        """グラフ要素のレンダリング"""
        elem = ChartElement(
            element_id="chart-1",
            type="chart",
            position=ElementPosition(x=0, y=0, width=500, height=300),
            chart_type="bar",
            data={"labels": ["A", "B", "C"], "values": [10, 20, 30]},
        )
        result = renderer._render_chart(elem)
        
        assert '<canvas' in result
        assert 'id="chart-1"' in result
        assert 'data-chart-type="bar"' in result
        assert 'data-chart-data=' in result

    def test_render_table_element(self, renderer):
        """表要素のレンダリング"""
        elem = TableElement(
            element_id="table-1",
            type="table",
            position=ElementPosition(x=0, y=0, width=400, height=200),
            rows=2,
            cols=3,
            cells=[["A", "B", "C"], ["1", "2", "3"]],
        )
        result = renderer._render_table(elem)
        
        assert '<table' in result
        assert 'id="table-1"' in result
        assert "<td>A</td>" in result
        assert "<td>1</td>" in result
        assert "<tr>" in result

    def test_render_element_dispatches_correctly(self, renderer):
        """_render_elementが正しく要素タイプごとに分岐する"""
        text_elem = TextElement(
            element_id="text",
            type="text",
            position=ElementPosition(x=0, y=0, width=100, height=50),
            content="Test",
        )
        result = renderer._render_element(text_elem)
        assert 'class="text-element"' in result

        img_elem = ImageElement(
            element_id="img",
            type="image",
            position=ElementPosition(x=0, y=0, width=100, height=50),
            source_url="https://example.com/img.jpg",
        )
        result = renderer._render_element(img_elem)
        assert 'class="image-element"' in result

    def test_render_page(self, renderer):
        """ページのレンダリング"""
        page = SlidePage(
            page_num=1,
            layout="title_slide",
            background=BackgroundStyle(color="#FFFFFF"),
            elements=[
                TextElement(
                    element_id="title",
                    type="text",
                    position=ElementPosition(x=100, y=100, width=600, height=100),
                    content="Page Title",
                )
            ],
            notes="This is a note",
        )
        result = renderer.render_page(page)
        
        assert 'data-page-num="1"' in result
        assert 'data-layout="title_slide"' in result
        assert "Page Title" in result
        assert "This is a note" in result
        assert "background-color: #FFFFFF" in result

    def test_render_page_without_notes(self, renderer):
        """ノートなしのページ"""
        page = SlidePage(
            page_num=2,
            layout="blank",
            elements=[],
        )
        result = renderer.render_page(page)
        
        assert 'data-page-num="2"' in result
        assert 'class="slide-notes"' not in result

    def test_render_presentation(self, renderer):
        """プレゼンテーション全体のレンダリング"""
        presentation = SlidePresentation(
            title="Test Presentation",
            pages=[
                SlidePage(
                    page_num=1,
                    layout="title_slide",
                    elements=[
                        TextElement(
                            element_id="title",
                            type="text",
                            position=ElementPosition(x=100, y=200, width=800, height=100),
                            content="Welcome",
                        )
                    ],
                ),
                SlidePage(
                    page_num=2,
                    layout="blank",
                    elements=[],
                ),
            ],
        )
        result = renderer.render_presentation(presentation)
        
        # HTML構造の検証
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "</html>" in result
        
        # タイトルの検証
        assert "Test Presentation" in result
        
        # ページ数の検証
        assert "全ページ数: 2" in result
        
        # スタイルとスクリプトの検証
        assert "<style>" in result
        assert "<script>" in result
        assert "Chart.js" in result
        
        # コンテンツの検証
        assert "Welcome" in result
        assert 'data-page-num="1"' in result
        assert 'data-page-num="2"' in result

    def test_render_presentation_escapes_title(self, renderer):
        """プレゼンテーションタイトルのHTMLエスケープ"""
        presentation = SlidePresentation(
            title="<script>alert('xss')</script>",
            pages=[
                SlidePage(page_num=1, layout="blank", elements=[])
            ],
        )
        result = renderer.render_presentation(presentation)
        
        assert "&lt;script&gt;" in result
        assert "<script>alert('xss')" not in result

    def test_get_base_styles(self, renderer):
        """基本CSSスタイルの取得"""
        styles = renderer._get_base_styles()
        
        assert "presentation-container" in styles
        assert "slide" in styles
        assert "text-element" in styles
        assert "image-element" in styles
        assert "table-element" in styles
        assert "@media" in styles  # レスポンシブ対応

    def test_get_base_scripts(self, renderer):
        """基本JavaScriptの取得"""
        scripts = renderer._get_base_scripts()
        
        assert "keydown" in scripts
        assert "ArrowLeft" in scripts
        assert "ArrowRight" in scripts
        assert "Chart" in scripts
        assert "DOMContentLoaded" in scripts


class TestIntegrationHTML:
    """HTML生成の統合テスト"""

    def test_complete_presentation_html(self):
        """完全なプレゼンテーションのHTML生成"""
        renderer = HTMLRenderer()
        
        presentation = SlidePresentation(
            title="Integration Test Presentation",
            pages=[
                SlidePage(
                    page_num=1,
                    layout="title_slide",
                    background=BackgroundStyle(color="#F0F0F0"),
                    elements=[
                        TextElement(
                            element_id="title",
                            type="text",
                            position=ElementPosition(x=100, y=200, width=800, height=100),
                            content="Integration Test",
                            style=TextStyle(font_size=48, font_weight="bold", align="center"),
                        ),
                    ],
                ),
                SlidePage(
                    page_num=2,
                    layout="title_content",
                    elements=[
                        TextElement(
                            element_id="heading",
                            type="text",
                            position=ElementPosition(x=50, y=50, width=900, height=80),
                            content="Content Page",
                        ),
                        ImageElement(
                            element_id="img",
                            type="image",
                            position=ElementPosition(x=100, y=150, width=400, height=300),
                            source_url="https://example.com/test.jpg",
                            alt_text="Test image",
                        ),
                        ShapeElement(
                            element_id="box",
                            type="shape",
                            position=ElementPosition(x=550, y=200, width=350, height=200),
                            shape_type="circle",
                            fill_color="#FF5733",
                        ),
                    ],
                ),
                SlidePage(
                    page_num=3,
                    layout="blank",
                    elements=[
                        TableElement(
                            element_id="data-table",
                            type="table",
                            position=ElementPosition(x=100, y=100, width=800, height=400),
                            rows=3,
                            cols=3,
                            cells=[
                                ["Header 1", "Header 2", "Header 3"],
                                ["Data 1", "Data 2", "Data 3"],
                                ["Data 4", "Data 5", "Data 6"],
                            ],
                        ),
                    ],
                    notes="Table slide with speaker notes",
                ),
            ],
            metadata={"version": "1.0.0"},
        )
        
        html = renderer.render_presentation(presentation)
        
        # 基本構造の検証
        assert html.startswith("<!DOCTYPE html>")
        assert html.endswith("</html>")
        
        # 各ページのコンテンツが含まれている
        assert "Integration Test" in html
        assert "Content Page" in html
        assert "Header 1" in html
        assert "Data 1" in html
        
        # 各要素のID が含まれている
        assert 'id="title"' in html
        assert 'id="heading"' in html
        assert 'id="img"' in html
        assert 'id="box"' in html
        assert 'id="data-table"' in html
        
        # スピーカーノートが含まれている
        assert "Table slide with speaker notes" in html
        
        # 背景色が適用されている
        assert "background-color: #F0F0F0" in html
        assert "background-color: #FF5733" in html
        
        # HTML as valid (basic check)
        assert html.count("<html") == 1
        assert html.count("</html>") == 1
        assert html.count("<body>") == 1
        assert html.count("</body>") == 1
