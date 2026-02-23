"""
Slide (Project) Application DTO
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


# ── Request ───────────────────────────────────────────


class CreateSlideDTO(BaseModel):
    title: str
    template_id: Optional[str] = None


class UpdateSlideDTO(BaseModel):
    title: Optional[str] = None


class CreateVersionDTO(BaseModel):
    slide_id: str


class CreatePageDTO(BaseModel):
    page_num: int
    contents: Any


class UpdatePageDTO(BaseModel):
    contents: Any


class SyncPageEditDTO(BaseModel):
    object_id: str
    text: str


class SyncPageEditsDTO(BaseModel):
    edits: list[SyncPageEditDTO]


# ── Response ──────────────────────────────────────────


class SlideResponseDTO(BaseModel):
    id: str
    owner_id: str
    template_id: Optional[str]
    title: str
    images: List[str]
    created_at: datetime
    updated_at: datetime


class SlideListItemDTO(BaseModel):
    id: str
    title: str
    template_id: Optional[str]
    images: List[str]
    updated_at: datetime


class SlideVersionResponseDTO(BaseModel):
    id: str
    slide_id: str
    version_num: int
    created_at: datetime


class PageResponseDTO(BaseModel):
    id: str
    slide_version_id: str
    page_num: int
    contents: Any
    created_at: datetime
    updated_at: datetime
