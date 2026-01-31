from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.db.project_service import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
)
from app.services.db.slot_service import update_slot, update_slots
from typing import Optional, List

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""
    template_id: str
    template_name: str


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class UpdateSlotRequest(BaseModel):
    value: Optional[str] = None
    status: Optional[str] = None
    linked_story_id: Optional[str] = None


class UpdateSlotsRequest(BaseModel):
    updates: List[dict]


@router.get("")
async def list_projects(db: Session = Depends(get_db)):
    """プロジェクト一覧を取得"""
    try:
        projects = get_projects(db)
        return {
            "success": True,
            "data": [project.dict() for project in projects],
        }
    except Exception as e:
        print(f"Error fetching projects: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch projects: {str(e)}",
        )


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """プロジェクトを取得"""
    try:
        project = get_project(db, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "success": True,
            "data": project.dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch project: {str(e)}",
        )


@router.post("")
async def create_new_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
):
    """プロジェクトを作成"""
    try:
        project = create_project(
            db,
            name=request.name,
            description=request.description,
            template_id=request.template_id,
            template_name=request.template_name,
        )
        
        return {
            "success": True,
            "data": project.dict(),
        }
    except Exception as e:
        print(f"Error creating project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project: {str(e)}",
        )


@router.patch("/{project_id}")
async def update_project_by_id(
    project_id: str = Path(...),
    request: UpdateProjectRequest = ...,
    db: Session = Depends(get_db),
):
    """プロジェクトを更新"""
    try:
        project = update_project(
            db,
            project_id,
            name=request.name,
            description=request.description,
            status=request.status,
        )
        
        return {
            "success": True,
            "data": project.dict(),
        }
    except Exception as e:
        print(f"Error updating project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update project: {str(e)}",
        )


@router.delete("/{project_id}")
async def delete_project_by_id(
    project_id: str = Path(...),
    db: Session = Depends(get_db),
):
    """プロジェクトを削除"""
    try:
        delete_project(db, project_id)
        
        return {
            "success": True,
            "message": "Project deleted successfully",
        }
    except Exception as e:
        print(f"Error deleting project: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete project: {str(e)}",
        )


@router.patch("/{project_id}/slots/{slot_id}")
async def update_slot_by_id(
    project_id: str = Path(...),
    slot_id: str = Path(...),
    request: UpdateSlotRequest = ...,
    db: Session = Depends(get_db),
):
    """スロットを更新"""
    try:
        slot = update_slot(
            db,
            project_id,
            slot_id,
            value=request.value,
            status=request.status,
            linked_story_id=request.linked_story_id,
        )
        
        return {
            "success": True,
            "data": slot.dict(),
        }
    except Exception as e:
        print(f"Error updating slot: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update slot: {str(e)}",
        )


@router.patch("/{project_id}/slots")
async def update_slots_bulk(
    project_id: str = Path(...),
    request: UpdateSlotsRequest = ...,
    db: Session = Depends(get_db),
):
    """スロットを一括更新"""
    try:
        slots = update_slots(db, project_id, request.updates)
        
        return {
            "success": True,
            "data": [slot.dict() for slot in slots],
        }
    except Exception as e:
        print(f"Error updating slots: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update slots: {str(e)}",
        )

