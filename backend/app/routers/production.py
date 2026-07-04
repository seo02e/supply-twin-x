from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.production import (
    ProductionCreate,
    ProductionUpdate,
    ProductionResponse,
)
from app.services import production_service

router = APIRouter(
    prefix="/productions",
    tags=["Productions"]
)


@router.post("/", response_model=ProductionResponse)
def create_production(
    production: ProductionCreate,
    db: Session = Depends(get_db),
):
    return production_service.create_production(db, production)


@router.get("/", response_model=list[ProductionResponse])
def get_productions(
    company_id: int,
    db: Session = Depends(get_db),
):
    return production_service.get_productions(db, company_id)


@router.get("/{production_id}", response_model=ProductionResponse)
def get_production(
    production_id: int,
    db: Session = Depends(get_db),
):
    production = production_service.get_production(db, production_id)

    if not production:
        raise HTTPException(status_code=404, detail="Production not found")

    return production


@router.put("/{production_id}", response_model=ProductionResponse)
def update_production(
    production_id: int,
    production: ProductionUpdate,
    db: Session = Depends(get_db),
):
    updated = production_service.update_production(
        db,
        production_id,
        production,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Production not found")

    return updated


@router.delete("/{production_id}")
def delete_production(
    production_id: int,
    db: Session = Depends(get_db),
):
    deleted = production_service.delete_production(db, production_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Production not found")

    return {"message": "Production deleted successfully"}