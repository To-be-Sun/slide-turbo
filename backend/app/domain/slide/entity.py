"""
Slide (Project) ドメインエンティティ
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class Slide(BaseModel):
    id: str
    owner_id: str
    template_id: Optional[str] = None
    title: str
    images: List[str] = []
    created_at: datetime
    updated_at: datetime


class SlideVersion(BaseModel):
    id: str
    slide_id: str
    version_num: int
    created_at: datetime


class Page(BaseModel):
    id: str
    slide_version_id: str
    page_num: int
    contents: Any
    created_at: datetime
    updated_at: datetime
