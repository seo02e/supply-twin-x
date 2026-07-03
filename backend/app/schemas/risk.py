from pydantic import BaseModel
from typing import List


class RiskFactor(BaseModel):
    name: str
    score: float
    reason: str


class RiskSummaryResponse(BaseModel):
    total_score: float
    risk_level: str
    oil_score: float
    inventory_score: float
    industry_score: float
    factors: List[RiskFactor]
    ai_report: str