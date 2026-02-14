"""
User Application DTO
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Request ───────────────────────────────────────────


class GoogleLoginDTO(BaseModel):
    code: str


class UpdateUserDTO(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None


# ── Response ──────────────────────────────────────────


class UserResponseDTO(BaseModel):
    id: str
    email: str
    name: str
    icon: Optional[str]
    created_at: datetime


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    google_access_token: str | None = None
    user: UserResponseDTO
