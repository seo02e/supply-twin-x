from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
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
):
    return inventory_service.create_inventory(db, inventory)


@router.get("/", response_model=list[InventoryResponse])
def get_inventories(
    db: Session = Depends(get_db),
):
    return inventory_service.get_inventories(db)


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    inventory = inventory_service.get_inventory(db, inventory_id)

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return inventory


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db),
):
    updated = inventory_service.update_inventory(
        db,
        inventory_id,
        inventory,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return updated


@router.delete("/{inventory_id}")
def delete_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
):
    deleted = inventory_service.delete_inventory(
        db,
        inventory_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return {"message": "Inventory deleted successfully"}