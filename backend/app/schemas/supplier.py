from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SupplierCreate(BaseModel):
    company_id: int
    supplier_name: str
    country: str
    material_name: str
    lead_time_days: int


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    country: Optional[str] = None
    material_name: Optional[str] = None
    lead_time_days: Optional[int] = None


class SupplierResponse(BaseModel):
    id: int
    company_id: int
    supplier_name: str
    country: str
    material_name: str
    lead_time_days: int
    created_at: datetime

    class Config:
        from_attributes = True