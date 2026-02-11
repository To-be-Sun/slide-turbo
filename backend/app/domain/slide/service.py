"""
Slide ドメインサービス
バージョニング・ページ順序などのビジネスルール。
"""

from app.domain.slide.entity import Page


class SlideService:
    """Slide に関するドメインロジック"""

    @staticmethod
    def validate_page_order(pages: list[Page]) -> bool:
        """ページ番号が 1 から連番であることを検証する。"""
        nums = sorted(p.page_num for p in pages)
        return nums == list(range(1, len(pages) + 1))

    @staticmethod
    def next_version_num(current_max: int) -> int:
        """次のバージョン番号を返す。"""
        return current_max + 1
