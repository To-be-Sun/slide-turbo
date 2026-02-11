"""
Outline (骨子) Application DTO
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Request ───────────────────────────────────────────


class CreateOutlineDTO(BaseModel):
    slide_version_id: str
    title: str
    description: str


class UpdateOutlineDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class RefineOutlineDTO(BaseModel):
    outline_id: str
    instructions: str


# ── Response ──────────────────────────────────────────


class OutlineResponseDTO(BaseModel):
    id: str
    slide_version_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
