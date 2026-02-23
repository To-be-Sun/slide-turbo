"""
Outline (骨子) Application DTO
"""

from datetime import datetime
from typing import Any, Optional

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


class GenerateSlideFromOutlineDTO(BaseModel):
    outline_id: str
    slide_object_id: str = "slide-mvp-001"
    image_url: Optional[str] = None
    page_num: Optional[int] = None
    total_pages: Optional[int] = None
    previous_slide_summary: Optional[str] = None


# ── Response ──────────────────────────────────────────


class OutlineResponseDTO(BaseModel):
    id: str
    slide_version_id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime


class SlideOutputResponseDTO(BaseModel):
    outline_id: str
    slide: Any
