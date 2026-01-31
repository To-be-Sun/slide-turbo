from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.db.template_service import (
    get_templates,
    get_template,
    create_template,
    update_template,
    delete_template,
)
from typing import Optional, List

router = APIRouter(prefix="/api/templates", tags=["templates"])


class CreateTemplateRequest(BaseModel):
    name: str
    description: str = ""
    thumbnail: str = ""
    slide_count: int
    html: Optional[str] = None
    slots: List[dict]


class UpdateTemplateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    slide_count: Optional[int] = None
    html: Optional[str] = None


@router.get("")
async def list_templates(db: Session = Depends(get_db)):
    """テンプレート一覧を取得"""
    try:
        templates = get_templates(db)
        return {
            "success": True,
            "data": [template.dict() for template in templates],
        }
    except Exception as e:
        print(f"Error fetching templates: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch templates: {str(e)}",
        )


@router.get("/{template_id}")
async def get_template_by_id(
    template_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """テンプレートを取得"""
    try:
        template = get_template(db, template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "data": template.dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch template: {str(e)}",
        )


@router.post("")
async def create_new_template(
    request: CreateTemplateRequest,
    db: Session = Depends(get_db),
):
    """テンプレートを作成"""
    try:
        template = create_template(
            db,
            name=request.name,
            description=request.description,
            thumbnail=request.thumbnail,
            slide_count=request.slide_count,
            html=request.html,
            slots=request.slots,
        )
        
        return {
            "success": True,
            "data": template.dict(),
        }
    except Exception as e:
        print(f"Error creating template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create template: {str(e)}",
        )


@router.patch("/{template_id}")
async def update_template_by_id(
    template_id: str = Path(...),
    request: UpdateTemplateRequest = ...,
    db: Session = Depends(get_db),
):
    """テンプレートを更新"""
    try:
        template = update_template(
            db,
            template_id,
            name=request.name,
            description=request.description,
            thumbnail=request.thumbnail,
            slide_count=request.slide_count,
            html=request.html,
        )
        
        return {
            "success": True,
            "data": template.dict(),
        }
    except Exception as e:
        print(f"Error updating template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update template: {str(e)}",
        )


@router.delete("/{template_id}")
async def delete_template_by_id(
    template_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """テンプレートを削除"""
    try:
        delete_template(db, template_id)
        
        return {
            "success": True,
            "message": "Template deleted successfully",
        }
    except Exception as e:
        print(f"Error deleting template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete template: {str(e)}",
        )

