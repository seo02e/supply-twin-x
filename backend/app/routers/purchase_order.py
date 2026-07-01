from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
)
from app.services import purchase_order_service

router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"]
)


@router.post("/", response_model=PurchaseOrderResponse)
def create_purchase_order(
    purchase_order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
):
    return purchase_order_service.create_purchase_order(db, purchase_order)


@router.get("/", response_model=list[PurchaseOrderResponse])
def get_purchase_orders(
    db: Session = Depends(get_db),
):
    return purchase_order_service.get_purchase_orders(db)


@router.get("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    purchase_order = purchase_order_service.get_purchase_order(
        db,
        purchase_order_id,
    )

    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return purchase_order


@router.put("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    purchase_order_id: int,
    purchase_order: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
):
    updated = purchase_order_service.update_purchase_order(
        db,
        purchase_order_id,
        purchase_order,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return updated


@router.delete("/{purchase_order_id}")
def delete_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
):
    deleted = purchase_order_service.delete_purchase_order(
        db,
        purchase_order_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return {"message": "Purchase order deleted successfully"}