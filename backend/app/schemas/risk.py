from pydantic import BaseModel
from typing import List, Optional


class RiskFactor(BaseModel):
    name: str
    score: float
    reason: str


class RiskSummaryResponse(BaseModel):
    total_score: float
    risk_level: str
    price_score: Optional[float]
    import_score: Optional[float]
    inventory_score: Optional[float]
    operation_score: Optional[float]
    oil_score: Optional[float]
    factors: List[RiskFactor]
    ai_report: str
