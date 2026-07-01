from pydantic import BaseModel
from typing import Optional


class CompanyCreate(BaseModel):
    company_name: str
    business_number: Optional[str] = None
    industry_type: Optional[str] = None
    complex_id: Optional[int] = None


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    business_number: Optional[str]
    industry_type: Optional[str]
    complex_id: Optional[int]

    class Config:
        from_attributes = True