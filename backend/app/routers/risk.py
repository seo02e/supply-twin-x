from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.risk import RiskSummaryResponse
from app.services.risk_service import calculate_risk_summary

router = APIRouter()


@router.get("/summary", response_model=RiskSummaryResponse)
def get_risk_summary(company_id: int = 1, db: Session = Depends(get_db)):
    return calculate_risk_summary(db, company_id)