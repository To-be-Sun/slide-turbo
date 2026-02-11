"""
User ドメインサービス
"""


class UserService:

    @staticmethod
    def validate_username(name: str) -> bool:
        """ユーザー名は 1〜50 文字"""
        return 1 <= len(name.strip()) <= 50
