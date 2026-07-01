from sqlalchemy.orm import Session

from app.models.models import PurchaseOrder
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
)


def create_purchase_order(db: Session, purchase_order: PurchaseOrderCreate):
    db_purchase_order = PurchaseOrder(**purchase_order.model_dump())

    db.add(db_purchase_order)
    db.commit()
    db.refresh(db_purchase_order)

    return db_purchase_order


def get_purchase_orders(db: Session):
    return db.query(PurchaseOrder).all()


def get_purchase_order(db: Session, purchase_order_id: int):
    return (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.id == purchase_order_id)
        .first()
    )


def update_purchase_order(
    db: Session,
    purchase_order_id: int,
    purchase_order: PurchaseOrderUpdate,
):
    db_purchase_order = get_purchase_order(db, purchase_order_id)

    if not db_purchase_order:
        return None

    update_data = purchase_order.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_purchase_order, key, value)

    db.commit()
    db.refresh(db_purchase_order)

    return db_purchase_order


def delete_purchase_order(db: Session, purchase_order_id: int):
    db_purchase_order = get_purchase_order(db, purchase_order_id)

    if not db_purchase_order:
        return None

    db.delete(db_purchase_order)
    db.commit()

    return db_purchase_order