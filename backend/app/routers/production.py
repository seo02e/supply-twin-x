from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
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
    current_user: User = Depends(get_current_user),
):
    return production_service.create_production(db, production, current_user.company_id)


@router.get("/", response_model=list[ProductionResponse])
def get_productions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return production_service.get_productions(db, current_user.company_id)


@router.get("/{production_id}", response_model=ProductionResponse)
def get_production(
    production_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    production = production_service.get_production(db, production_id)

    if not production or production.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Production not found")

    return production


@router.put("/{production_id}", response_model=ProductionResponse)
def update_production(
    production_id: int,
    production: ProductionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = production_service.get_production(db, production_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Production not found")

    return production_service.update_production(
        db,
        production_id,
        production,
    )


@router.delete("/{production_id}")
def delete_production(
    production_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = production_service.get_production(db, production_id)

    if not existing or existing.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Production not found")

    production_service.delete_production(db, production_id)

    return {"message": "Production deleted successfully"}