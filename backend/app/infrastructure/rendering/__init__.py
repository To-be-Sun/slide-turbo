"""
rendering package initialization
"""
from app.infrastructure.rendering.html_renderer import HTMLRenderer
from app.infrastructure.rendering.schema import (
    SlidePage,
    SlidePresentation,
    TextElement,
    ImageElement,
    ShapeElement,
    ChartElement,
    TableElement,
    ElementPosition,
    TextStyle,
    BackgroundStyle,
)

__all__ = [
    "HTMLRenderer",
    "SlidePage",
    "SlidePresentation",
    "TextElement",
    "ImageElement",
    "ShapeElement",
    "ChartElement",
    "TableElement",
    "ElementPosition",
    "TextStyle",
    "BackgroundStyle",
]
