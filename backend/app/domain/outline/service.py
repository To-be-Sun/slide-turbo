"""
Outline ドメインサービス
骨子の構造検証・整合性チェックロジック。
"""


class OutlineService:
    """Outline に関するドメインロジック"""

    @staticmethod
    def validate_outline(title: str, description: str) -> bool:
        """骨子の最低限のバリデーション"""
        return len(title.strip()) > 0 and len(description.strip()) > 0
