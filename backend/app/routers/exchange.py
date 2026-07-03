from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.exchange_service import fetch_and_save_usd_krw, get_latest_usd_krw

router = APIRouter(prefix="/exchange", tags=["Exchange"])


@router.post("/fetch-usd")
def fetch_usd_exchange(search_date: str | None = None, db: Session = Depends(get_db)):
    try:
        return fetch_and_save_usd_krw(db, search_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usd")
def latest_usd_exchange(db: Session = Depends(get_db)):
    data = get_latest_usd_krw(db)

    if not data:
        raise HTTPException(status_code=404, detail="저장된 USD 환율 데이터가 없습니다.")

    return data