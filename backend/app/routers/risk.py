from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
from app.schemas.risk import RiskSummaryResponse
from app.services.risk_service import calculate_company_risk

router = APIRouter()


@router.get("/summary", response_model=RiskSummaryResponse)
def get_risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return calculate_company_risk(current_user.company_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
