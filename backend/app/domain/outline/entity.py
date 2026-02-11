"""
Outline (骨子) ドメインエンティティ
プレゼンの骨組みを定義する。マルチエージェントが生成・推敲する対象。
"""

from datetime import datetime

from pydantic import BaseModel


class Outline(BaseModel):
    """骨子 — SlideVersion に紐づくプレゼンの構成要素"""

    id: str
    slide_version_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
