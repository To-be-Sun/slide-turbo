"""
User ドメインエンティティ
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    name: str
    icon: Optional[str] = None
    google_id: str
    created_at: datetime
    updated_at: datetime
