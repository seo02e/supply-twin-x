from datetime import date
from typing import Optional

from pydantic import BaseModel


class OilPriceLatestResponse(BaseModel):
    observation_date: date
    price: float
    change_rate: Optional[float] = None


class OilPriceHistoryItem(BaseModel):
    observation_date: date
    price: float
