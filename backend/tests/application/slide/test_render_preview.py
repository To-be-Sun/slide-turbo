"""
SlideUseCases.render_preview のテスト
"""

import pytest
from unittest.mock import AsyncMock, Mock

from app.application.slide.usecases import SlideUseCases
from app.domain.slide.entity import Slide, SlideVersion, Page
from app.shared.exceptions import NotFoundException


class TestRenderPreview:
    """render_preview メソッドのテスト"""

    @pytest.fixture
    def mock_repo(self):
        """モックリポジトリ"""
        return Mock()

    @pytest.fixture
    def usecases(self, mock_repo):
        """SlideUseCases インスタンス"""
        return SlideUseCases(repo=mock_repo)

    @pytest.mark.asyncio
    async def test_render_preview_success(self, usecases, mock_repo):
        """正常なHTMLプレビュー生成"""
        # モックデータ準備
        slide = Slide(
            id="slide-1",
            owner_id="user-1",
            template_id="template-1",
            title="Test Slide",
            images=[],
        )
        version = SlideVersion(
            id="version-1", slide_id="slide-1", version_num=1
        )
        page1 = Page(
            id="page-1",
            slide_version_id="version-1",
            page_num=1,
            contents={
                "pageNum": 1,
                "layout": "TITLE_SLIDE",
                "elements": [
                    {
                        "type": "text",
                        "position": {"x": 10, "y": 10, "width": 100, "height": 50},
                        "content": "Hello World",
                    }
                ],
            },
        )

        # モック設定
        mock_repo.find_slide_by_id = AsyncMock(return_value=slide)
        mock_repo.find_version_by_num = AsyncMock(return_value=version)
        mock_repo.find_pages_by_version = AsyncMock(return_value=[page1])

        # 実行
        html = await usecases.render_preview("slide-1", 1)

        # 検証
        assert "<html" in html
        assert "Test Slide" in html
        assert "Hello World" in html
        mock_repo.find_slide_by_id.assert_called_once_with("slide-1")
        mock_repo.find_version_by_num.assert_called_once_with("slide-1", 1)
        mock_repo.find_pages_by_version.assert_called_once_with("version-1")

    @pytest.mark.asyncio
    async def test_render_preview_slide_not_found(self, usecases, mock_repo):
        """スライドが存在しない場合"""
        mock_repo.find_slide_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exc_info:
            await usecases.render_preview("invalid-slide", 1)

        assert "Slide invalid-slide not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_render_preview_version_not_found(self, usecases, mock_repo):
        """バージョンが存在しない場合"""
        slide = Slide(
            id="slide-1",
            owner_id="user-1",
            template_id="template-1",
            title="Test Slide",
            images=[],
        )

        mock_repo.find_slide_by_id = AsyncMock(return_value=slide)
        mock_repo.find_version_by_num = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exc_info:
            await usecases.render_preview("slide-1", 999)

        assert "Version 999 not found for slide slide-1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_render_preview_empty_pages(self, usecases, mock_repo):
        """ページがない場合でも空のプレゼンテーションを生成"""
        slide = Slide(
            id="slide-1",
            owner_id="user-1",
            template_id="template-1",
            title="Empty Slide",
            images=[],
        )
        version = SlideVersion(
            id="version-1", slide_id="slide-1", version_num=1
        )

        mock_repo.find_slide_by_id = AsyncMock(return_value=slide)
        mock_repo.find_version_by_num = AsyncMock(return_value=version)
        mock_repo.find_pages_by_version = AsyncMock(return_value=[])

        # 実行
        html = await usecases.render_preview("slide-1", 1)

        # 検証
        assert "<html" in html
        assert "Empty Slide" in html

    @pytest.mark.asyncio
    async def test_render_preview_multiple_pages(self, usecases, mock_repo):
        """複数ページの場合"""
        slide = Slide(
            id="slide-1",
            owner_id="user-1",
            template_id="template-1",
            title="Multi Page",
            images=[],
        )
        version = SlideVersion(
            id="version-1", slide_id="slide-1", version_num=1
        )
        page1 = Page(
            id="page-1",
            slide_version_id="version-1",
            page_num=1,
            contents={
                "pageNum": 1,
                "layout": "TITLE_SLIDE",
                "elements": [
                    {
                        "type": "text",
                        "position": {"x": 10, "y": 10, "width": 100, "height": 50},
                        "content": "Page 1",
                    }
                ],
            },
        )
        page2 = Page(
            id="page-2",
            slide_version_id="version-1",
            page_num=2,
            contents={
                "pageNum": 2,
                "layout": "CONTENT_SLIDE",
                "elements": [
                    {
                        "type": "text",
                        "position": {"x": 10, "y": 10, "width": 100, "height": 50},
                        "content": "Page 2",
                    }
                ],
            },
        )

        mock_repo.find_slide_by_id = AsyncMock(return_value=slide)
        mock_repo.find_version_by_num = AsyncMock(return_value=version)
        mock_repo.find_pages_by_version = AsyncMock(return_value=[page1, page2])

        # 実行
        html = await usecases.render_preview("slide-1", 1)

        # 検証
        assert "<html" in html
        assert "Page 1" in html
        assert "Page 2" in html
