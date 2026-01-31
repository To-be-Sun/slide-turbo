from typing import Optional, List, Literal
from pydantic import BaseModel
from datetime import datetime


# Template types
class TemplateSlot(BaseModel):
    id: str
    slide_index: int
    name: str
    type: Literal["title", "text", "image", "chart", "list", "icon"]
    placeholder: str
    required: bool


class Template(BaseModel):
    id: str
    name: str
    description: str
    thumbnail: str
    slide_count: int
    slots: List[TemplateSlot]
    created_at: datetime


# Filled Slot types
class FilledSlot(BaseModel):
    slot_id: str
    slide_index: int
    name: str
    type: Literal["title", "text", "image", "chart", "list", "icon"]
    value: str
    status: Literal["empty", "draft", "filled", "approved"]
    linked_story_id: Optional[str] = None


# Story Section types
class StorySection(BaseModel):
    id: str
    title: str
    content: str
    slide_indices: List[int]
    status: Literal["draft", "approved"]
    order: int


# Project Material types
class ProjectMaterial(BaseModel):
    id: str
    name: str
    type: Literal["icon", "image", "text", "chart"]
    content: str
    tags: List[str]
    used_in_slots: List[str] = []


# Project Version types
class ProjectVersion(BaseModel):
    id: str
    name: str
    description: str
    slots: List[dict] = []
    story: List[dict] = []
    created_at: datetime


# Suggestion types
class Suggestion(BaseModel):
    id: str
    type: Literal["slot-update", "story-sync", "material-add"]
    message: str
    source_slot_id: Optional[str] = None
    target_slot_ids: List[str] = []
    suggested_value: Optional[str] = None
    dismissed: bool
    created_at: datetime


# Project types
class Project(BaseModel):
    id: str
    name: str
    description: str
    template_id: str
    template_name: str
    status: Literal["draft", "in-progress", "completed"]
    slots: List[FilledSlot]
    story: List[StorySection] = []
    materials: List[ProjectMaterial] = []
    versions: List[ProjectVersion] = []
    suggestions: List[Suggestion] = []
    created_at: datetime
    updated_at: datetime


# API Request/Response types
class GenerateSlideRequest(BaseModel):
    template_id: str
    slots: List[FilledSlot]
    story: Optional[List[StorySection]] = None


class SlideData(BaseModel):
    slide_index: int
    html: str
    image_url: Optional[str] = None


class GenerateSlideResponse(BaseModel):
    html: str
    slides: List[SlideData]


class FillSlotRequest(BaseModel):
    slot_id: str
    value: str
    context: Optional[dict] = None


class FillSlotResponse(BaseModel):
    value: str
    html: str


# Slide Review types
class SuggestedSlot(BaseModel):
    id: str
    name: str
    type: Literal["title", "text", "image", "chart", "list", "icon"]
    placeholder: str
    required: bool


class SlideReview(BaseModel):
    title: str
    description: str
    suggested_slots: List[SuggestedSlot]
    improvements: Optional[List[str]] = None


class PresentationReview(BaseModel):
    title: str
    description: str
    slide_reviews: List[SlideReview]

