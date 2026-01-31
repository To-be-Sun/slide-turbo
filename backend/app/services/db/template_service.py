from sqlalchemy.orm import Session
from app.database import TemplateModel, TemplateSlotModel
from app.types import Template, TemplateSlot
from typing import List, Optional


def get_template(db: Session, template_id: str) -> Optional[Template]:
    """テンプレートを取得"""
    template = (
        db.query(TemplateModel)
        .filter(TemplateModel.id == template_id)
        .first()
    )
    
    if not template:
        return None
    
    return Template(
        id=template.id,
        name=template.name,
        description=template.description,
        thumbnail=template.thumbnail,
        slide_count=template.slide_count,
        slots=[
            TemplateSlot(
                id=slot.id,
                slide_index=slot.slide_index,
                name=slot.name,
                type=slot.type.value,
                placeholder=slot.placeholder,
                required=slot.required,
            )
            for slot in sorted(template.slots, key=lambda s: (s.slide_index, s.created_at))
        ],
        created_at=template.created_at,
    )


def get_templates(db: Session) -> List[Template]:
    """テンプレート一覧を取得"""
    templates = db.query(TemplateModel).order_by(TemplateModel.created_at.desc()).all()
    
    return [
        Template(
            id=template.id,
            name=template.name,
            description=template.description,
            thumbnail=template.thumbnail,
            slide_count=template.slide_count,
            slots=[
                TemplateSlot(
                    id=slot.id,
                    slide_index=slot.slide_index,
                    name=slot.name,
                    type=slot.type.value,
                    placeholder=slot.placeholder,
                    required=slot.required,
                )
                for slot in sorted(template.slots, key=lambda s: (s.slide_index, s.created_at))
            ],
            created_at=template.created_at,
        )
        for template in templates
    ]


def create_template(
    db: Session,
    name: str,
    description: str,
    thumbnail: str,
    slide_count: int,
    html: Optional[str] = None,
    slots: Optional[List[dict]] = None,
) -> Template:
    """テンプレートを作成"""
    template = TemplateModel(
        name=name,
        description=description,
        thumbnail=thumbnail,
        slide_count=slide_count,
        html=html,
    )
    
    if slots:
        template.slots = [
            TemplateSlotModel(
                slide_index=slot["slide_index"],
                name=slot["name"],
                type=slot["type"],
                placeholder=slot.get("placeholder", ""),
                required=slot.get("required", False),
            )
            for slot in slots
        ]
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return get_template(db, template.id)


def update_template(
    db: Session,
    template_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    thumbnail: Optional[str] = None,
    slide_count: Optional[int] = None,
    html: Optional[str] = None,
) -> Template:
    """テンプレートを更新"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if not template:
        raise ValueError("Template not found")
    
    if name is not None:
        template.name = name
    if description is not None:
        template.description = description
    if thumbnail is not None:
        template.thumbnail = thumbnail
    if slide_count is not None:
        template.slide_count = slide_count
    if html is not None:
        template.html = html
    
    db.commit()
    db.refresh(template)
    
    return get_template(db, template.id)


def delete_template(db: Session, template_id: str) -> None:
    """テンプレートを削除"""
    template = db.query(TemplateModel).filter(TemplateModel.id == template_id).first()
    if template:
        db.delete(template)
        db.commit()

