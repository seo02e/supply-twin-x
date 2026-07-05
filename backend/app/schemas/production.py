from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
from typing import Optional


class ProductionCreate(BaseModel):
    product_name: str
    production_quantity: Decimal
    operation_rate: Decimal
    production_date: date


class ProductionUpdate(BaseModel):
    product_name: Optional[str] = None
    production_quantity: Optional[Decimal] = None
    operation_rate: Optional[Decimal] = None
    production_date: Optional[date] = None


class ProductionResponse(BaseModel):
    id: int
    company_id: int
    product_name: str
    production_quantity: Decimal
    operation_rate: Decimal
    production_date: date
    created_at: datetime

    class Config:
        from_attributes = True