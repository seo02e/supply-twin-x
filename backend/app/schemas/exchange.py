from pydantic import BaseModel
from datetime import date
from typing import Optional


class ExchangeRateResponse(BaseModel):
    currency_code: str
    currency_name: Optional[str] = None
    base_rate: float
    rate_date: date