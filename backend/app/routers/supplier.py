from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
)
from app.services import supplier_service

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return supplier_service.create_supplier(db, supplier, current_user.company_id)


@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return supplier_service.get_suppliers(db, current_user.company_id)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier = supplier_service.get_supplier(db, supplier_id)

    if not supplier or supplier.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = supplier_service.get_supplier(db, supplier_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return supplier_service.update_supplier(db, supplier_id, supplier)


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = supplier_service.get_supplier(db, supplier_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier_service.delete_supplier(db, supplier_id)

    return {"message": "Supplier deleted successfully"}