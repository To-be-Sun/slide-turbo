from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, Enum as SQLEnum, ARRAY, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class SlotType(PyEnum):
    title = "title"
    text = "text"
    image = "image"
    chart = "chart"
    list = "list"
    icon = "icon"


class SlotStatus(PyEnum):
    EMPTY = "EMPTY"
    draft = "draft"
    filled = "filled"
    approved = "approved"


class ProjectStatus(PyEnum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    completed = "completed"


class StoryStatus(PyEnum):
    DRAFT = "DRAFT"
    approved = "approved"


class MaterialType(PyEnum):
    icon = "icon"
    image = "image"
    text = "text"
    chart = "chart"


class SuggestionType(PyEnum):
    slot_update = "slot_update"
    story_sync = "story_sync"
    material_add = "material_add"


class ChatRole(PyEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class HistoryType(PyEnum):
    project = "project"
    template = "template"
    slot = "slot"
    story = "story"
    version = "version"


# Models
class TemplateModel(Base):
    __tablename__ = "templates"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    slide_count = Column(Integer, default=0)
    html = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    slots = relationship("TemplateSlotModel", back_populates="template", cascade="all, delete-orphan")
    projects = relationship("ProjectModel", back_populates="template")
    
    __table_args__ = (
        Index("idx_template_created", "created_at"),
    )


class TemplateSlotModel(Base):
    __tablename__ = "template_slots"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(UUID(as_uuid=False), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    slide_index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(SlotType), nullable=False)
    placeholder = Column(String, default="")
    required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("TemplateModel", back_populates="slots")
    filled_slots = relationship("FilledSlotModel", back_populates="template_slot", foreign_keys="FilledSlotModel.slot_id")


class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, default="")
    template_id = Column(UUID(as_uuid=False), ForeignKey("templates.id"), nullable=False)
    template_name = Column(String, nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    template = relationship("TemplateModel", back_populates="projects")
    slots = relationship("FilledSlotModel", back_populates="project", cascade="all, delete-orphan")
    story_sections = relationship("StorySectionModel", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("ProjectMaterialModel", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("ProjectVersionModel", back_populates="project", cascade="all, delete-orphan")
    suggestions = relationship("SuggestionModel", back_populates="project", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessageModel", back_populates="project", cascade="all, delete-orphan")
    history_items = relationship("HistoryItemModel", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_project_template", "template_id"),
        Index("idx_project_status", "status"),
        Index("idx_project_created", "created_at"),
    )


class FilledSlotModel(Base):
    __tablename__ = "filled_slots"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(UUID(as_uuid=False), ForeignKey("template_slots.id"), nullable=False)
    slide_index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(SlotType), nullable=False)
    value = Column(Text, default="")
    status = Column(SQLEnum(SlotStatus), default=SlotStatus.EMPTY)
    linked_story_id = Column(UUID(as_uuid=False), ForeignKey("story_sections.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="slots")
    template_slot = relationship("TemplateSlotModel", back_populates="filled_slots", foreign_keys=[slot_id])
    linked_story = relationship("StorySectionModel", back_populates="linked_slots", foreign_keys=[linked_story_id])
    
    __table_args__ = (
        UniqueConstraint("project_id", "slot_id", name="uq_project_slot"),
        Index("idx_project_slide", "project_id", "slide_index"),
        Index("idx_slot_id", "slot_id"),
        Index("idx_linked_story", "linked_story_id"),
    )


class StorySectionModel(Base):
    __tablename__ = "story_sections"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    slide_indices = Column(ARRAY(Integer), nullable=False)
    status = Column(SQLEnum(StoryStatus), default=StoryStatus.DRAFT)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="story_sections")
    linked_slots = relationship("FilledSlotModel", back_populates="linked_story", foreign_keys="[FilledSlotModel.linked_story_id]")
    
    __table_args__ = (
        Index("idx_project_order", "project_id", "order"),
    )


class ProjectMaterialModel(Base):
    __tablename__ = "project_materials"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(MaterialType), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="materials")
    
    __table_args__ = (
        Index("idx_project_material", "project_id"),
        Index("idx_material_type", "type"),
    )


class ProjectVersionModel(Base):
    __tablename__ = "project_versions"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="versions")
    
    __table_args__ = (
        Index("idx_version_project", "project_id", "created_at"),
    )


class SuggestionModel(Base):
    __tablename__ = "suggestions"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(SuggestionType), nullable=False)
    message = Column(Text, nullable=False)
    source_slot_id = Column(UUID(as_uuid=False), ForeignKey("filled_slots.id"), nullable=True)
    target_slot_ids = Column(ARRAY(String), default=[])
    suggested_value = Column(Text, nullable=True)
    dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="suggestions")
    source_slot = relationship("FilledSlotModel", foreign_keys=[source_slot_id])
    
    __table_args__ = (
        Index("idx_suggestion_project", "project_id", "dismissed"),
        Index("idx_suggestion_source", "source_slot_id"),
    )


class ChatMessageModel(Base):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(ChatRole), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="chat_messages")
    
    __table_args__ = (
        Index("idx_chat_project", "project_id", "timestamp"),
    )


class HistoryItemModel(Base):
    __tablename__ = "history_items"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    type = Column(SQLEnum(HistoryType), nullable=False)
    action = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("ProjectModel", back_populates="history_items")
    
    __table_args__ = (
        Index("idx_history_project", "project_id", "timestamp"),
        Index("idx_history_type", "type"),
    )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

