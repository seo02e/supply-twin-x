from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.oil import OilPriceHistoryItem, OilPriceLatestResponse
from app.services import oil_service

router = APIRouter(prefix="/oil", tags=["Oil"])


@router.get("/latest", response_model=OilPriceLatestResponse)
def get_latest_oil_price(db: Session = Depends(get_db)):
    data = oil_service.get_latest_oil_price(db)

    if not data:
        raise HTTPException(status_code=404, detail="저장된 원유 가격 데이터가 없습니다.")

    return data


@router.get("/history", response_model=list[OilPriceHistoryItem])
def get_oil_price_history(months: int = 12, db: Session = Depends(get_db)):
    return oil_service.get_oil_price_history(db, months)
