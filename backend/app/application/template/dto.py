"""
Template Application DTO
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


# ── Request ───────────────────────────────────────────


class CreateTemplateDTO(BaseModel):
    title: str
    contents: Any


class ImportFromGoogleSlidesDTO(BaseModel):
    presentation_url: str


class UpdateTemplateDTO(BaseModel):
    title: Optional[str] = None
    contents: Optional[Any] = None


# ── Response ──────────────────────────────────────────


class TemplateResponseDTO(BaseModel):
    id: str
    owner_id: str
    title: str
    contents: Any
    created_at: datetime
    updated_at: datetime


class TemplateListItemDTO(BaseModel):
    id: str
    title: str
    created_at: datetime
