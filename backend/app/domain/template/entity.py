"""
Template ドメインエンティティ
Google Slides からインポートされた、または手動作成されたスライドテンプレート。
contents には JSON でスライドレイアウト定義が格納される。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Template(BaseModel):
    id: str
    owner_id: str
    title: str
    contents: Any  # JSON: テンプレートのレイアウト構造
    created_at: datetime
    updated_at: datetime
