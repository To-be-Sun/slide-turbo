"""
Google Slides Exporter のテスト
リファクタリング後のコードが正しく動作するか確認
"""

import pytest
from app.infrastructure.google_slides.exporter import (
    hex_to_rgb,
    px_to_pt,
    LAYOUT_MAPPING,
    SHAPE_TYPE_MAPPING,
    TEXT_ALIGN_MAPPING,
    PX_TO_PT_RATIO,
)


class TestHelperFunctions:
    """ヘルパー関数のテスト"""

    def test_hex_to_rgb_6_digits(self):
        """6桁HEX (#RRGGBB) のRGB変換"""
        result = hex_to_rgb("#FF0000")
        assert result == {"red": 1.0, "green": 0.0, "blue": 0.0}

        result = hex_to_rgb("#00FF00")
        assert result == {"red": 0.0, "green": 1.0, "blue": 0.0}

        result = hex_to_rgb("#0000FF")
        assert result == {"red": 0.0, "green": 0.0, "blue": 1.0}

    def test_hex_to_rgb_3_digits(self):
        """3桁HEX (#RGB) のRGB変換"""
        result = hex_to_rgb("#F00")
        assert result == {"red": 1.0, "green": 0.0, "blue": 0.0}

        result = hex_to_rgb("#0F0")
        assert result == {"red": 0.0, "green": 1.0, "blue": 0.0}

    def test_hex_to_rgb_without_hash(self):
        """# なしのHEX変換"""
        result = hex_to_rgb("FF0000")
        assert result == {"red": 1.0, "green": 0.0, "blue": 0.0}

    def test_hex_to_rgb_grayscale(self):
        """グレースケールのRGB変換"""
        result = hex_to_rgb("#808080")
        assert abs(result["red"] - 0.5019607843137255) < 0.0001
        assert abs(result["green"] - 0.5019607843137255) < 0.0001
        assert abs(result["blue"] - 0.5019607843137255) < 0.0001

    def test_px_to_pt_conversion(self):
        """ピクセルからポイントへの変換"""
        assert px_to_pt(100) == 75.0  # 100 * 0.75
        assert px_to_pt(200) == 150.0  # 200 * 0.75
        assert px_to_pt(0) == 0.0
        assert px_to_pt(1) == 0.75

    def test_px_to_pt_ratio_constant(self):
        """PX_TO_PT_RATIO定数の値確認"""
        assert PX_TO_PT_RATIO == 0.75


class TestConstants:
    """定数のテスト"""

    def test_layout_mapping_exists(self):
        """レイアウトマッピングが定義されている"""
        assert "title_slide" in LAYOUT_MAPPING
        assert "title_content" in LAYOUT_MAPPING
        assert "two_column" in LAYOUT_MAPPING
        assert "blank" in LAYOUT_MAPPING
        assert "image_full" in LAYOUT_MAPPING

    def test_layout_mapping_values(self):
        """レイアウトマッピングの値が正しい"""
        assert LAYOUT_MAPPING["title_slide"] == "TITLE"
        assert LAYOUT_MAPPING["title_content"] == "TITLE_AND_BODY"
        assert LAYOUT_MAPPING["two_column"] == "TITLE_AND_TWO_COLUMNS"
        assert LAYOUT_MAPPING["blank"] == "BLANK"
        assert LAYOUT_MAPPING["image_full"] == "BLANK"

    def test_shape_type_mapping_exists(self):
        """図形タイプマッピングが定義されている"""
        assert "rectangle" in SHAPE_TYPE_MAPPING
        assert "circle" in SHAPE_TYPE_MAPPING
        assert "triangle" in SHAPE_TYPE_MAPPING

    def test_shape_type_mapping_values(self):
        """図形タイプマッピングの値が正しい"""
        assert SHAPE_TYPE_MAPPING["rectangle"] == "RECTANGLE"
        assert SHAPE_TYPE_MAPPING["circle"] == "ELLIPSE"
        assert SHAPE_TYPE_MAPPING["triangle"] == "TRIANGLE"

    def test_text_align_mapping_exists(self):
        """テキスト配置マッピングが定義されている"""
        assert "left" in TEXT_ALIGN_MAPPING
        assert "center" in TEXT_ALIGN_MAPPING
        assert "right" in TEXT_ALIGN_MAPPING

    def test_text_align_mapping_values(self):
        """テキスト配置マッピングの値が正しい"""
        assert TEXT_ALIGN_MAPPING["left"] == "START"
        assert TEXT_ALIGN_MAPPING["center"] == "CENTER"
        assert TEXT_ALIGN_MAPPING["right"] == "END"


class TestGoogleSlidesExporterBasics:
    """GoogleSlidesExporter クラスの基本テスト"""

    def test_exporter_class_exists(self):
        """GoogleSlidesExporter クラスがインポート可能"""
        from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
        assert GoogleSlidesExporter is not None

    def test_exporter_has_export_presentation_method(self):
        """export_presentation メソッドが存在する"""
        from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
        assert hasattr(GoogleSlidesExporter, "export_presentation")

    def test_exporter_has_private_methods(self):
        """プライベートメソッドが存在する"""
        from app.infrastructure.google_slides.exporter import GoogleSlidesExporter
        
        assert hasattr(GoogleSlidesExporter, "_build_slide_requests")
        assert hasattr(GoogleSlidesExporter, "_build_element_requests")
        assert hasattr(GoogleSlidesExporter, "_build_element_properties")
        assert hasattr(GoogleSlidesExporter, "_build_text_requests")
        assert hasattr(GoogleSlidesExporter, "_build_image_requests")
        assert hasattr(GoogleSlidesExporter, "_build_shape_requests")
        assert hasattr(GoogleSlidesExporter, "_build_table_requests")
