"""
Template ドメインサービス
テンプレートのバリデーション・構造検証ロジック。
"""

from typing import Any


class TemplateService:
    """Template に関するドメインロジック"""

    @staticmethod
    def validate_contents(contents: Any) -> bool:
        """
        テンプレートの contents JSON が有効な構造か検証する。
        TODO: contents のスキーマが確定したら実装
        """
        if not isinstance(contents, (dict, list)):
            return False
        return True

    @staticmethod
    def extract_slot_keys(contents: Any) -> list[str]:
        """
        contents JSON からスロットキー（差し替え可能フィールド）を抽出する。
        TODO: contents のフォーマット確定後に実装
        """
        return []
