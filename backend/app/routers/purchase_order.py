from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
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
    current_user: User = Depends(get_current_user),
):
    return purchase_order_service.create_purchase_order(db, purchase_order, current_user.company_id)


@router.get("/", response_model=list[PurchaseOrderResponse])
def get_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return purchase_order_service.get_purchase_orders(db, current_user.company_id)


@router.get("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    purchase_order = purchase_order_service.get_purchase_order(
        db,
        purchase_order_id,
    )

    if not purchase_order or purchase_order.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return purchase_order


@router.put("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    purchase_order_id: int,
    purchase_order: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = purchase_order_service.get_purchase_order(db, purchase_order_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return purchase_order_service.update_purchase_order(
        db,
        purchase_order_id,
        purchase_order,
    )


@router.delete("/{purchase_order_id}")
def delete_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = purchase_order_service.get_purchase_order(db, purchase_order_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    purchase_order_service.delete_purchase_order(db, purchase_order_id)

    return {"message": "Purchase order deleted successfully"}