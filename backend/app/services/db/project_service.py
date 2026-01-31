from sqlalchemy.orm import Session
from app.database import (
    ProjectModel,
    FilledSlotModel,
    StorySectionModel,
    ProjectMaterialModel,
    ProjectVersionModel,
    SuggestionModel,
    TemplateModel,
    SlotStatus,
    ProjectStatus,
)
from app.types import Project, FilledSlot, StorySection
from typing import List, Optional


def get_project(db: Session, project_id: str) -> Optional[Project]:
    """プロジェクトを取得"""
    project = (
        db.query(ProjectModel)
        .filter(ProjectModel.id == project_id)
        .first()
    )
    
    if not project:
        return None
    
    # 関連データを取得
    slots = (
        db.query(FilledSlotModel)
        .filter(FilledSlotModel.project_id == project_id)
        .order_by(FilledSlotModel.slide_index, FilledSlotModel.created_at)
        .all()
    )
    
    story_sections = (
        db.query(StorySectionModel)
        .filter(StorySectionModel.project_id == project_id)
        .order_by(StorySectionModel.order)
        .all()
    )
    
    materials = (
        db.query(ProjectMaterialModel)
        .filter(ProjectMaterialModel.project_id == project_id)
        .order_by(ProjectMaterialModel.created_at.desc())
        .all()
    )
    
    versions = (
        db.query(ProjectVersionModel)
        .filter(ProjectVersionModel.project_id == project_id)
        .order_by(ProjectVersionModel.created_at.desc())
        .all()
    )
    
    suggestions = (
        db.query(SuggestionModel)
        .filter(
            SuggestionModel.project_id == project_id,
            SuggestionModel.dismissed == False,
        )
        .order_by(SuggestionModel.created_at.desc())
        .all()
    )
    
    return Project(
        id=project.id,
        name=project.name,
        description=project.description,
        template_id=project.template_id,
        template_name=project.template_name,
        status=project.status.value.lower().replace("_", "-"),
        slots=[
            FilledSlot(
                slot_id=slot.slot_id,
                slide_index=slot.slide_index,
                name=slot.name,
                type=slot.type.value,
                value=slot.value,
                status=slot.status.value.lower(),
                linked_story_id=slot.linked_story_id,
            )
            for slot in slots
        ],
        story=[
            StorySection(
                id=story.id,
                title=story.title,
                content=story.content,
                slide_indices=story.slide_indices,
                status=story.status.value.lower(),
                order=story.order,
            )
            for story in story_sections
        ],
        materials=[],  # TODO: 実装
        versions=[],  # TODO: 実装
        suggestions=[],  # TODO: 実装
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def get_projects(db: Session) -> List[Project]:
    """プロジェクト一覧を取得"""
    projects = (
        db.query(ProjectModel)
        .order_by(ProjectModel.updated_at.desc())
        .all()
    )
    
    result = []
    for project in projects:
        slots = (
            db.query(FilledSlotModel)
            .filter(FilledSlotModel.project_id == project.id)
            .all()
        )
        
        result.append(
            Project(
                id=project.id,
                name=project.name,
                description=project.description,
                template_id=project.template_id,
                template_name=project.template_name,
                status=project.status.value.lower().replace("_", "-"),
                slots=[
                    FilledSlot(
                        slot_id=slot.slot_id,
                        slide_index=slot.slide_index,
                        name=slot.name,
                        type=slot.type.value,
                        value=slot.value,
                        status=slot.status.value.lower(),
                        linked_story_id=slot.linked_story_id,
                    )
                    for slot in slots
                ],
                story=[],
                materials=[],
                versions=[],
                suggestions=[],
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )
    
    return result


def create_project(
    db: Session,
    name: str,
    description: str,
    template_id: str,
    template_name: str,
) -> Project:
    """プロジェクトを作成"""
    # テンプレートのスロットを取得
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise ValueError("Template not found")
    
    # プロジェクトを作成し、初期スロットも作成
    project = ProjectModel(
        name=name,
        description=description,
        template_id=template_id,
        template_name=template_name,
        status=ProjectStatus.DRAFT,
    )
    
    db.add(project)
    db.flush()
    
    # スロットを作成
    for slot in template.slots:
        filled_slot = FilledSlotModel(
            project_id=project.id,
            slot_id=slot.id,
            slide_index=slot.slide_index,
            name=slot.name,
            type=slot.type,
            value="",
            status=SlotStatus.EMPTY,
        )
        db.add(filled_slot)
    
    db.commit()
    db.refresh(project)
    
    return get_project(db, project.id)


def update_project(
    db: Session,
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> Project:
    """プロジェクトを更新"""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if status is not None:
        project.status = ProjectStatus[status.upper().replace("-", "_")]
    
    db.commit()
    db.refresh(project)
    
    return get_project(db, project.id)


def delete_project(db: Session, project_id: str) -> None:
    """プロジェクトを削除"""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()

