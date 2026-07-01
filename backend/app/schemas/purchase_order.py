from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
from typing import Optional


class PurchaseOrderCreate(BaseModel):
    company_id: int
    supplier_id: Optional[int] = None
    material_name: str
    quantity: Decimal
    order_date: date
    expected_arrival_date: date
    status: str


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    material_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    order_date: Optional[date] = None
    expected_arrival_date: Optional[date] = None
    status: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    id: int
    company_id: int
    supplier_id: Optional[int] = None
    material_name: str
    quantity: Decimal
    order_date: date
    expected_arrival_date: date
    status: str
    created_at: datetime

    class Config:
        from_attributes = True