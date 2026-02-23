"""
スライドレンダリング用のPydanticモデル定義
エージェントが出力するJSON構造を型安全に扱うためのスキーマ
"""

from typing import Literal, Optional, Any, Union
from pydantic import BaseModel, Field


class ElementPosition(BaseModel):
    """要素の位置とサイズ"""
    x: float
    y: float
    width: float
    height: float


class TextStyle(BaseModel):
    """テキストスタイル"""
    font_family: str = "Arial"
    font_size: float = 16
    font_weight: Literal["normal", "bold"] = "normal"
    color: str = "#000000"
    align: Literal["left", "center", "right"] = "left"
    line_height: float = 1.5


class BackgroundStyle(BaseModel):
    """背景スタイル"""
    color: Optional[str] = None
    image_url: Optional[str] = None


class SlideElement(BaseModel):
    """スライド要素の基底クラス"""
    element_id: str
    type: Literal["text", "image", "shape", "chart", "table"]
    position: ElementPosition
    z_index: int = 0


class TextElement(SlideElement):
    """テキスト要素"""
    type: Literal["text"] = "text"
    content: str
    style: TextStyle = Field(default_factory=TextStyle)
    placeholder: Optional[str] = None


class ImageElement(SlideElement):
    """画像要素"""
    type: Literal["image"] = "image"
    source_url: str
    alt_text: str = ""
    placeholder: Optional[str] = None


class ShapeElement(SlideElement):
    """図形要素"""
    type: Literal["shape"] = "shape"
    shape_type: Literal["rectangle", "circle", "triangle"]
    fill_color: str = "#CCCCCC"
    border_color: Optional[str] = None
    border_width: float = 0


class ChartElement(SlideElement):
    """グラフ要素"""
    type: Literal["chart"] = "chart"
    chart_type: Literal["bar", "line", "pie"]
    data: dict[str, Any]


class TableElement(SlideElement):
    """表要素"""
    type: Literal["table"] = "table"
    rows: int
    cols: int
    cells: list[list[str]]


class SlidePage(BaseModel):
    """単一のスライドページ"""
    page_num: int = Field(ge=1, description="ページ番号（1以上）")
    layout: Literal["title_slide", "title_content", "two_column", "blank", "image_full"]
    background: BackgroundStyle = Field(default_factory=BackgroundStyle)
    elements: list[Union[TextElement, ImageElement, ShapeElement, ChartElement, TableElement]]
    notes: Optional[str] = None


class SlidePresentation(BaseModel):
    """プレゼンテーション全体"""
    title: str
    pages: list[SlidePage] = Field(min_length=1, description="最低1ページ必要")
    metadata: dict[str, Any] = Field(default_factory=dict)
