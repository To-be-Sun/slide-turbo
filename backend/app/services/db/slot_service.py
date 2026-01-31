from sqlalchemy.orm import Session
from app.database import FilledSlotModel, SlotStatus
from app.types import FilledSlot
from typing import List, Optional


def update_slot(
    db: Session,
    project_id: str,
    slot_id: str,
    value: Optional[str] = None,
    status: Optional[str] = None,
    linked_story_id: Optional[str] = None,
) -> FilledSlot:
    """スロットを更新"""
    slot = (
        db.query(FilledSlotModel)
        .filter(
            FilledSlotModel.id == slot_id,
            FilledSlotModel.project_id == project_id,
        )
        .first()
    )
    
    if not slot:
        raise ValueError("Slot not found")
    
    if value is not None:
        slot.value = value
    if status is not None:
        slot.status = SlotStatus[status.upper()]
    if linked_story_id is not None:
        slot.linked_story_id = linked_story_id
    
    db.commit()
    db.refresh(slot)
    
    return FilledSlot(
        slot_id=slot.slot_id,
        slide_index=slot.slide_index,
        name=slot.name,
        type=slot.type.value,
        value=slot.value,
        status=slot.status.value.lower(),
        linked_story_id=slot.linked_story_id,
    )


def update_slots(
    db: Session,
    project_id: str,
    updates: List[dict],
) -> List[FilledSlot]:
    """スロットを一括更新"""
    results = []
    for update in updates:
        slot = update_slot(
            db,
            project_id,
            update["slot_id"],
            value=update.get("value"),
            status=update.get("status"),
        )
        results.append(slot)
    
    return results

