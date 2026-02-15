"""
Tests for rendering schema (Pydantic models)
"""

import pytest
from pydantic import ValidationError
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


class TestElementPosition:
    """ElementPosition model tests"""

    def test_valid_position(self):
        """正常な位置データ"""
        pos = ElementPosition(x=100.0, y=200.0, width=300.0, height=150.0)
        assert pos.x == 100.0
        assert pos.y == 200.0
        assert pos.width == 300.0
        assert pos.height == 150.0

    def test_negative_values_allowed(self):
        """負の値も許可される"""
        pos = ElementPosition(x=-10.0, y=-20.0, width=100.0, height=50.0)
        assert pos.x == -10.0
        assert pos.y == -20.0


class TestTextStyle:
    """TextStyle model tests"""

    def test_default_values(self):
        """デフォルト値のテスト"""
        style = TextStyle()
        assert style.font_family == "Arial"
        assert style.font_size == 16
        assert style.font_weight == "normal"
        assert style.color == "#000000"
        assert style.align == "left"
        assert style.line_height == 1.5

    def test_custom_values(self):
        """カスタム値のテスト"""
        style = TextStyle(
            font_family="Helvetica",
            font_size=24,
            font_weight="bold",
            color="#FF0000",
            align="center",
            line_height=2.0,
        )
        assert style.font_family == "Helvetica"
        assert style.font_size == 24
        assert style.font_weight == "bold"
        assert style.color == "#FF0000"
        assert style.align == "center"
        assert style.line_height == 2.0

    def test_invalid_font_weight(self):
        """無効なfont_weightは拒否される"""
        with pytest.raises(ValidationError):
            TextStyle(font_weight="extra-bold")

    def test_invalid_align(self):
        """無効なalignは拒否される"""
        with pytest.raises(ValidationError):
            TextStyle(align="justify")


class TestBackgroundStyle:
    """BackgroundStyle model tests"""

    def test_empty_background(self):
        """空の背景"""
        bg = BackgroundStyle()
        assert bg.color is None
        assert bg.image_url is None

    def test_color_only(self):
        """色のみ"""
        bg = BackgroundStyle(color="#FFFFFF")
        assert bg.color == "#FFFFFF"
        assert bg.image_url is None

    def test_image_only(self):
        """画像URLのみ"""
        bg = BackgroundStyle(image_url="https://example.com/bg.jpg")
        assert bg.color is None
        assert bg.image_url == "https://example.com/bg.jpg"


class TestTextElement:
    """TextElement model tests"""

    def test_minimal_text_element(self):
        """最小限のテキスト要素"""
        elem = TextElement(
            element_id="text-1",
            type="text",
            position=ElementPosition(x=0, y=0, width=100, height=50),
            content="Hello World",
        )
        assert elem.element_id == "text-1"
        assert elem.type == "text"
        assert elem.content == "Hello World"
        assert elem.style.font_family == "Arial"  # default
        assert elem.placeholder is None

    def test_text_with_custom_style(self):
        """カスタムスタイル付きテキスト"""
        elem = TextElement(
            element_id="text-2",
            type="text",
            position=ElementPosition(x=10, y=20, width=200, height=100),
            content="Styled Text",
            style=TextStyle(font_size=32, color="#FF0000", font_weight="bold"),
        )
        assert elem.style.font_size == 32
        assert elem.style.color == "#FF0000"
        assert elem.style.font_weight == "bold"

    def test_text_with_placeholder(self):
        """プレースホルダー付きテキスト"""
        elem = TextElement(
            element_id="text-3",
            type="text",
            position=ElementPosition(x=0, y=0, width=100, height=50),
            content="",
            placeholder="Enter title here",
        )
        assert elem.placeholder == "Enter title here"


class TestImageElement:
    """ImageElement model tests"""

    def test_minimal_image_element(self):
        """最小限の画像要素"""
        elem = ImageElement(
            element_id="img-1",
            type="image",
            position=ElementPosition(x=0, y=0, width=400, height=300),
            source_url="https://example.com/image.jpg",
        )
        assert elem.element_id == "img-1"
        assert elem.type == "image"
        assert elem.source_url == "https://example.com/image.jpg"
        assert elem.alt_text == ""  # default

    def test_image_with_alt_text(self):
        """alt_text付き画像"""
        elem = ImageElement(
            element_id="img-2",
            type="image",
            position=ElementPosition(x=0, y=0, width=400, height=300),
            source_url="https://example.com/logo.png",
            alt_text="Company Logo",
        )
        assert elem.alt_text == "Company Logo"


class TestShapeElement:
    """ShapeElement model tests"""

    def test_rectangle_shape(self):
        """矩形図形"""
        elem = ShapeElement(
            element_id="shape-1",
            type="shape",
            position=ElementPosition(x=50, y=50, width=200, height=100),
            shape_type="rectangle",
        )
        assert elem.shape_type == "rectangle"
        assert elem.fill_color == "#CCCCCC"  # default

    def test_circle_shape(self):
        """円形図形"""
        elem = ShapeElement(
            element_id="shape-2",
            type="shape",
            position=ElementPosition(x=100, y=100, width=150, height=150),
            shape_type="circle",
            fill_color="#FF0000",
        )
        assert elem.shape_type == "circle"
        assert elem.fill_color == "#FF0000"

    def test_shape_with_border(self):
        """ボーダー付き図形"""
        elem = ShapeElement(
            element_id="shape-3",
            type="shape",
            position=ElementPosition(x=0, y=0, width=100, height=100),
            shape_type="rectangle",
            border_color="#000000",
            border_width=2.0,
        )
        assert elem.border_color == "#000000"
        assert elem.border_width == 2.0


class TestChartElement:
    """ChartElement model tests"""

    def test_bar_chart(self):
        """棒グラフ"""
        elem = ChartElement(
            element_id="chart-1",
            type="chart",
            position=ElementPosition(x=0, y=0, width=500, height=300),
            chart_type="bar",
            data={"labels": ["A", "B", "C"], "values": [10, 20, 30]},
        )
        assert elem.chart_type == "bar"
        assert elem.data["labels"] == ["A", "B", "C"]


class TestTableElement:
    """TableElement model tests"""

    def test_simple_table(self):
        """シンプルな表"""
        elem = TableElement(
            element_id="table-1",
            type="table",
            position=ElementPosition(x=0, y=0, width=400, height=200),
            rows=2,
            cols=3,
            cells=[["A", "B", "C"], ["1", "2", "3"]],
        )
        assert elem.rows == 2
        assert elem.cols == 3
        assert len(elem.cells) == 2
        assert len(elem.cells[0]) == 3


class TestSlidePage:
    """SlidePage model tests"""

    def test_minimal_page(self):
        """最小限のページ（要素なし）"""
        page = SlidePage(
            page_num=1,
            layout="blank",
            elements=[],
        )
        assert page.page_num == 1
        assert page.layout == "blank"
        assert len(page.elements) == 0
        assert page.notes is None

    def test_page_with_text_element(self):
        """テキスト要素付きページ"""
        page = SlidePage(
            page_num=1,
            layout="title_content",
            elements=[
                TextElement(
                    element_id="text-1",
                    type="text",
                    position=ElementPosition(x=100, y=100, width=600, height=100),
                    content="Title Text",
                )
            ],
        )
        assert len(page.elements) == 1
        assert page.elements[0].content == "Title Text"

    def test_page_with_background(self):
        """背景付きページ"""
        page = SlidePage(
            page_num=2,
            layout="blank",
            background=BackgroundStyle(color="#F0F0F0"),
            elements=[],
        )
        assert page.background.color == "#F0F0F0"

    def test_page_with_notes(self):
        """ノート付きページ"""
        page = SlidePage(
            page_num=3,
            layout="blank",
            elements=[],
            notes="This is a speaker note",
        )
        assert page.notes == "This is a speaker note"

    def test_invalid_page_num_zero(self):
        """page_num=0は拒否される"""
        with pytest.raises(ValidationError):
            SlidePage(page_num=0, layout="blank", elements=[])

    def test_invalid_page_num_negative(self):
        """負のpage_numは拒否される"""
        with pytest.raises(ValidationError):
            SlidePage(page_num=-1, layout="blank", elements=[])

    def test_invalid_layout(self):
        """無効なlayoutは拒否される"""
        with pytest.raises(ValidationError):
            SlidePage(page_num=1, layout="invalid_layout", elements=[])


class TestSlidePresentation:
    """SlidePresentation model tests"""

    def test_minimal_presentation(self):
        """最小限のプレゼンテーション（1ページ）"""
        presentation = SlidePresentation(
            title="Test Presentation",
            pages=[
                SlidePage(page_num=1, layout="title_slide", elements=[])
            ],
        )
        assert presentation.title == "Test Presentation"
        assert len(presentation.pages) == 1
        assert presentation.metadata == {}

    def test_multi_page_presentation(self):
        """複数ページのプレゼンテーション"""
        presentation = SlidePresentation(
            title="Multi Page Presentation",
            pages=[
                SlidePage(page_num=1, layout="title_slide", elements=[]),
                SlidePage(page_num=2, layout="title_content", elements=[]),
                SlidePage(page_num=3, layout="blank", elements=[]),
            ],
        )
        assert len(presentation.pages) == 3

    def test_presentation_with_metadata(self):
        """メタデータ付きプレゼンテーション"""
        presentation = SlidePresentation(
            title="Presentation with Metadata",
            pages=[SlidePage(page_num=1, layout="blank", elements=[])],
            metadata={"author": "John Doe", "version": "1.0"},
        )
        assert presentation.metadata["author"] == "John Doe"
        assert presentation.metadata["version"] == "1.0"

    def test_empty_pages_rejected(self):
        """ページ数0は拒否される"""
        with pytest.raises(ValidationError):
            SlidePresentation(title="Empty Presentation", pages=[])


class TestIntegration:
    """統合テスト"""

    def test_complete_presentation(self):
        """完全なプレゼンテーションの作成"""
        presentation = SlidePresentation(
            title="Complete Presentation Example",
            pages=[
                SlidePage(
                    page_num=1,
                    layout="title_slide",
                    background=BackgroundStyle(color="#FFFFFF"),
                    elements=[
                        TextElement(
                            element_id="title",
                            type="text",
                            position=ElementPosition(x=100, y=200, width=800, height=100),
                            content="Welcome to the Presentation",
                            style=TextStyle(font_size=48, font_weight="bold", align="center"),
                        ),
                        TextElement(
                            element_id="subtitle",
                            type="text",
                            position=ElementPosition(x=100, y=350, width=800, height=50),
                            content="A comprehensive guide",
                            style=TextStyle(font_size=24, align="center"),
                        ),
                    ],
                    notes="Introduction slide",
                ),
                SlidePage(
                    page_num=2,
                    layout="title_content",
                    elements=[
                        TextElement(
                            element_id="heading",
                            type="text",
                            position=ElementPosition(x=50, y=50, width=900, height=80),
                            content="Key Points",
                            style=TextStyle(font_size=36, font_weight="bold"),
                        ),
                        ImageElement(
                            element_id="diagram",
                            type="image",
                            position=ElementPosition(x=100, y=150, width=400, height=300),
                            source_url="https://example.com/diagram.png",
                            alt_text="Process diagram",
                        ),
                        ShapeElement(
                            element_id="box",
                            type="shape",
                            position=ElementPosition(x=550, y=200, width=350, height=200),
                            shape_type="rectangle",
                            fill_color="#E0E0E0",
                        ),
                    ],
                ),
            ],
            metadata={"created_at": "2026-02-15", "version": "1.0.0"},
        )

        # 検証
        assert presentation.title == "Complete Presentation Example"
        assert len(presentation.pages) == 2
        
        # ページ1の検証
        page1 = presentation.pages[0]
        assert page1.page_num == 1
        assert len(page1.elements) == 2
        assert page1.elements[0].content == "Welcome to the Presentation"
        assert page1.notes == "Introduction slide"
        
        # ページ2の検証
        page2 = presentation.pages[1]
        assert page2.page_num == 2
        assert len(page2.elements) == 3
        assert isinstance(page2.elements[0], TextElement)
        assert isinstance(page2.elements[1], ImageElement)
        assert isinstance(page2.elements[2], ShapeElement)
