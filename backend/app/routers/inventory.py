from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
)
from app.services import inventory_service

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.post("/", response_model=InventoryResponse)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return inventory_service.create_inventory(db, inventory, current_user.company_id)


@router.get("/", response_model=list[InventoryResponse])
def get_inventories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return inventory_service.get_inventories(db, current_user.company_id)


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inventory = inventory_service.get_inventory(db, inventory_id)

    if not inventory or inventory.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return inventory


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = inventory_service.get_inventory(db, inventory_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Inventory not found")

    updated = inventory_service.update_inventory(
        db,
        inventory_id,
        inventory,
    )

    return updated


@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = inventory_service.get_inventory(db, inventory_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Inventory not found")

    inventory_service.delete_inventory(db, inventory_id)

    return {"message": "Inventory deleted successfully"}