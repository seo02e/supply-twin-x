from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.risk import RiskSummaryResponse
from app.services.risk_service import calculate_company_risk

router = APIRouter()


@router.get("/summary", response_model=RiskSummaryResponse)
def get_risk_summary(company_id: int = 1, db: Session = Depends(get_db)):
    try:
        return calculate_company_risk(company_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
