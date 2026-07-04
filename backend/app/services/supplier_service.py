from sqlalchemy.orm import Session

from app.models.models import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, supplier: SupplierCreate, company_id: int):
    db_supplier = Supplier(**supplier.model_dump(), company_id=company_id)

    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)

    return db_supplier


def get_suppliers(db: Session, company_id: int):
    return (
        db.query(Supplier)
        .filter(Supplier.company_id == company_id)
        .all()
    )


def get_supplier(db: Session, supplier_id: int):
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def update_supplier(db: Session, supplier_id: int, supplier: SupplierUpdate):
    db_supplier = get_supplier(db, supplier_id)

    if not db_supplier:
        return None

    update_data = supplier.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_supplier, key, value)

    db.commit()
    db.refresh(db_supplier)

    return db_supplier


def delete_supplier(db: Session, supplier_id: int):
    db_supplier = get_supplier(db, supplier_id)

    if not db_supplier:
        return None

    db.delete(db_supplier)
    db.commit()

    return db_supplier