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


class CompanyPublic(BaseModel):
    """회원가입 시 회사 선택용 — business_number는 가입 검증에 쓰이므로 노출하지 않음."""

    id: int
    company_name: str

    class Config:
        from_attributes = True