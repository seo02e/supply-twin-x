from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional


class InventoryCreate(BaseModel):
    company_id: int
    material_name: str
    current_stock: Decimal
    safety_stock: Decimal
    daily_usage: Decimal
    unit: str
    hs_code: Optional[str] = None


class InventoryUpdate(BaseModel):
    material_name: Optional[str] = None
    current_stock: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None
    daily_usage: Optional[Decimal] = None
    unit: Optional[str] = None
    hs_code: Optional[str] = None


class InventoryResponse(BaseModel):
    id: int
    company_id: int
    material_name: str
    current_stock: Decimal
    safety_stock: Decimal
    daily_usage: Decimal
    unit: str
    updated_at: datetime
    hs_code: str | None = None

    class Config:
        from_attributes = True