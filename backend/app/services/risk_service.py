import json
import logging
import os
from datetime import date, datetime, timedelta
from typing import Optional

import anthropic
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.models import Company, RiskHistory

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. 원자재 가격 점수 (0~100)
# ─────────────────────────────────────────────
def calc_price_score(material_name: str, db: Session) -> Optional[float]:
    """
    material_prices 최근 30일 가격 변동률 + 환율 변동률 * 0.5
    combined 변동률 20% = 100점 기준 선형 스케일링, 0~100 clip
    """
    cutoff = date.today() - timedelta(days=30)

    rows = db.execute(text("""
        SELECT price, price_date
        FROM material_prices
        WHERE material_name = :material_name
          AND price_date >= :cutoff
        ORDER BY price_date ASC
    """), {"material_name": material_name, "cutoff": cutoff}).mappings().all()

    if len(rows) < 2:
        return None

    first_price = float(rows[0]["price"])
    last_price = float(rows[-1]["price"])

    if first_price == 0:
        return None

    material_change = ((last_price - first_price) / first_price) * 100

    # 환율(USD/KRW) 변동률 — exchange_rates 테이블에서 최근 2건
    exchange_rows = db.execute(text("""
        SELECT base_rate
        FROM exchange_rates
        WHERE currency_code = 'USD'
        ORDER BY rate_date DESC
        LIMIT 2
    """)).mappings().all()

    exchange_change = 0.0
    if len(exchange_rows) == 2:
        latest_rate = float(exchange_rows[0]["base_rate"])
        prev_rate = float(exchange_rows[1]["base_rate"])
        if prev_rate != 0:
            exchange_change = ((latest_rate - prev_rate) / prev_rate) * 100

    combined = material_change + exchange_change * 0.5
    score = min(100.0, max(0.0, combined / 20.0 * 100.0))
    return round(score, 2)


# ─────────────────────────────────────────────
# 2. 수입 리스크 점수 (0~100)
# ─────────────────────────────────────────────
def calc_import_score(hs_code: str, db: Session) -> Optional[float]:
    """
    customs_trades 최근 3개월 import_amount 추세
    수입 감소율이 클수록 높은 점수 (감소 20% = 100점)
    """
    rows = db.execute(text("""
        SELECT trade_month, SUM(import_amount) AS total_import
        FROM customs_trades
        WHERE hs_code = :hs_code
        GROUP BY trade_month
        ORDER BY trade_month DESC
        LIMIT 3
    """), {"hs_code": hs_code}).mappings().all()

    if len(rows) < 2:
        return None

    latest = float(rows[0]["total_import"] or 0)
    oldest = float(rows[-1]["total_import"] or 0)

    if oldest == 0:
        return None

    change_rate = ((latest - oldest) / oldest) * 100  # 양수=증가, 음수=감소
    # 감소가 위험 → 부호 반전 후 스케일링
    score = min(100.0, max(0.0, (-change_rate) / 20.0 * 100.0))
    return round(score, 2)


# ─────────────────────────────────────────────
# 3. 재고 리스크 점수 (0~100)
# ─────────────────────────────────────────────
def calc_inventory_score(material_name: str, company_id: int, db: Session) -> Optional[float]:
    """
    소진예상일수 = (current_stock - safety_stock) / daily_usage
    30일 이상 = 0점, 0일 이하 = 100점 선형
    """
    row = db.execute(text("""
        SELECT current_stock, safety_stock, daily_usage
        FROM inventories
        WHERE material_name = :material_name
          AND company_id = :company_id
        LIMIT 1
    """), {"material_name": material_name, "company_id": company_id}).mappings().first()

    if not row:
        return None

    current = float(row["current_stock"] or 0)
    safety = float(row["safety_stock"] or 0)
    daily = float(row["daily_usage"] or 0)

    if daily == 0:
        return None

    days_remaining = (current - safety) / daily
    score = min(100.0, max(0.0, (1.0 - days_remaining / 30.0) * 100.0))
    return round(score, 2)


# ─────────────────────────────────────────────
# 4. 가동률 리스크 점수 (0~100)
# ─────────────────────────────────────────────
def calc_operation_score(complex_name: str, db: Session) -> Optional[float]:
    """
    가동률 80% 기준 미달분 → 0~50점
    생산변화율 음수 → 0~50점 (20% 감소 = 50점)
    합산 0~100점
    """
    row = db.execute(text("""
        SELECT operation_rate_current, production_change_rate
        FROM industry_trends
        WHERE complex_name = :complex_name
          AND operation_rate_current IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """), {"complex_name": complex_name}).mappings().first()

    if not row:
        return None

    op_rate = float(row["operation_rate_current"] or 0)
    prod_change = float(row["production_change_rate"] or 0)

    op_component = min(50.0, max(0.0, (80.0 - op_rate) / 80.0 * 50.0))
    prod_component = min(50.0, max(0.0, (-prod_change) / 20.0 * 50.0))

    return round(min(100.0, op_component + prod_component), 2)


# ─────────────────────────────────────────────
# 가중 평균 헬퍼 — None 축 제외 후 나머지 가중치로 재분배
# ─────────────────────────────────────────────
def _weighted_score(scores_weights: list[tuple[Optional[float], float]]) -> float:
    valid = [(s, w) for s, w in scores_weights if s is not None]
    if not valid:
        return 0.0
    total_weight = sum(w for _, w in valid)
    return sum(s * (w / total_weight) for s, w in valid)


# ─────────────────────────────────────────────
# 캐시 조회 — 동일 company_id + risk_level의 24시간 이내 최근 결과 반환
# ─────────────────────────────────────────────
def _get_cached_report(company_id: int, risk_level: str, db: Session) -> Optional[dict]:
    cutoff = datetime.utcnow() - timedelta(hours=24)
    row = db.execute(text("""
        SELECT reason, recommendation
        FROM risk_histories
        WHERE company_id = :company_id
          AND risk_level = :risk_level
          AND created_at >= :cutoff
        ORDER BY created_at DESC
        LIMIT 1
    """), {"company_id": company_id, "risk_level": risk_level, "cutoff": cutoff}).mappings().first()

    if row and row["reason"] and row["recommendation"]:
        return {"reason": row["reason"], "recommendation": row["recommendation"]}
    return None


# ─────────────────────────────────────────────
# 폴백 리포트 — Claude API 오류 시 여기로 복귀
# ─────────────────────────────────────────────
def _fallback_ai_report(
    total_score: float,
    risk_level: str,
    price_score: Optional[float],
    import_score: Optional[float],
    inventory_score: Optional[float],
    operation_score: Optional[float],
) -> dict:
    reason_parts = []
    rec_parts = []

    if price_score is not None:
        reason_parts.append(f"원자재 가격 위험도 {price_score:.1f}점")
        if price_score >= 60:
            rec_parts.append("원자재 가격 상승세 지속 시 선구매 또는 대체 공급처 확보를 검토하세요.")

    if import_score is not None:
        reason_parts.append(f"수입 감소 위험도 {import_score:.1f}점")
        if import_score >= 60:
            rec_parts.append("수입량 감소 추세가 감지됩니다. 수입처 다변화를 권장합니다.")

    if inventory_score is not None:
        reason_parts.append(f"재고 소진 위험도 {inventory_score:.1f}점")
        if inventory_score >= 60:
            rec_parts.append("안전재고 이하 품목의 즉시 발주를 검토하세요.")

    if operation_score is not None:
        reason_parts.append(f"가동률 위험도 {operation_score:.1f}점")
        if operation_score >= 60:
            rec_parts.append("산업단지 가동률 하락이 감지됩니다. 생산 일정 재점검을 권장합니다.")

    reason = (
        f"현재 공급망 위험도는 {risk_level} 단계({total_score:.1f}점)입니다. "
        + " / ".join(reason_parts)
    )
    recommendation = (
        " ".join(rec_parts) if rec_parts else "현재 공급망 상태를 지속적으로 모니터링하세요."
    )
    return {"reason": reason, "recommendation": recommendation}


# ─────────────────────────────────────────────
# Claude API 리포트 — 실패 시 _fallback_ai_report 반환
# ─────────────────────────────────────────────
def _llm_ai_report(
    total_score: float,
    risk_level: str,
    price_score: Optional[float],
    import_score: Optional[float],
    inventory_score: Optional[float],
    operation_score: Optional[float],
) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_ai_report(total_score, risk_level, price_score, import_score, inventory_score, operation_score)

    def _fmt_score(v: Optional[float]) -> str:
        return f"{v:.1f}점" if v is not None else "데이터 없음"

    user_content = (
        f"공급망 위험도 분석 결과:\n"
        f"- 총점: {total_score:.1f}점 ({risk_level})\n"
        f"- 원자재 가격 점수: {_fmt_score(price_score)}\n"
        f"- 수입 동향 점수: {_fmt_score(import_score)}\n"
        f"- 재고 점수: {_fmt_score(inventory_score)}\n"
        f"- 가동률 점수: {_fmt_score(operation_score)}\n"
    )

    try:
        client = anthropic.Anthropic(api_key=api_key, timeout=3.0)
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=512,
            system='공급망 리스크 분석가입니다. 반드시 JSON 형식으로만 응답하세요. {"reason": "...", "recommendation": "..."}',
            messages=[{"role": "user", "content": user_content}],
        )
        result = json.loads(response.content[0].text)
        if "reason" in result and "recommendation" in result:
            return result
    except Exception as exc:
        logger.warning("Claude API 오류, 폴백 사용: %s", exc)

    return _fallback_ai_report(total_score, risk_level, price_score, import_score, inventory_score, operation_score)


# ─────────────────────────────────────────────
# 최종 진입점
# ─────────────────────────────────────────────
def calculate_company_risk(company_id: int, db: Session) -> dict:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"company_id={company_id} 를 찾을 수 없습니다.")

    inventories = company.inventories
    complex_name = (
        company.industrial_complex.complex_name
        if company.industrial_complex else None
    )

    price_scores, import_scores, inventory_scores = [], [], []

    for inv in inventories:
        ps = calc_price_score(inv.material_name, db)
        if ps is not None:
            price_scores.append(ps)

        if inv.hs_code:
            im = calc_import_score(inv.hs_code, db)
            if im is not None:
                import_scores.append(im)

        iv = calc_inventory_score(inv.material_name, company_id, db)
        if iv is not None:
            inventory_scores.append(iv)

    price_score = round(sum(price_scores) / len(price_scores), 2) if price_scores else None
    import_score = round(sum(import_scores) / len(import_scores), 2) if import_scores else None
    inventory_score = round(sum(inventory_scores) / len(inventory_scores), 2) if inventory_scores else None
    operation_score = calc_operation_score(complex_name, db) if complex_name else None

    total_score = round(_weighted_score([
        (price_score, 0.3),
        (import_score, 0.2),
        (inventory_score, 0.3),
        (operation_score, 0.2),
    ]), 2)

    if total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    cached = _get_cached_report(company_id, risk_level, db)
    if cached:
        report = cached
    else:
        report = _llm_ai_report(
            total_score, risk_level,
            price_score, import_score, inventory_score, operation_score,
        )

    material_names = ",".join(inv.material_name for inv in inventories if inv.material_name)

    db.execute(text("""
        INSERT INTO risk_histories (
            company_id, material_name, risk_score, risk_level,
            price_score, import_score, inventory_score, operation_score,
            reason, recommendation
        ) VALUES (
            :company_id, :material_name, :risk_score, :risk_level,
            :price_score, :import_score, :inventory_score, :operation_score,
            :reason, :recommendation
        )
    """), {
        "company_id": company_id,
        "material_name": material_names or None,
        "risk_score": total_score,
        "risk_level": risk_level,
        "price_score": price_score,
        "import_score": import_score,
        "inventory_score": inventory_score,
        "operation_score": operation_score,
        "reason": report["reason"],
        "recommendation": report["recommendation"],
    })
    db.commit()

    def _fmt(v):
        return round(v, 2) if v is not None else None

    return {
        "total_score": total_score,
        "risk_level": risk_level,
        "price_score": _fmt(price_score),
        "import_score": _fmt(import_score),
        "inventory_score": _fmt(inventory_score),
        "operation_score": _fmt(operation_score),
        "factors": [
            {
                "name": "원자재 가격",
                "score": _fmt(price_score) or 0.0,
                "reason": f"{price_score:.1f}점" if price_score is not None else "데이터 없음",
            },
            {
                "name": "수입 동향",
                "score": _fmt(import_score) or 0.0,
                "reason": f"{import_score:.1f}점" if import_score is not None else "데이터 없음",
            },
            {
                "name": "재고",
                "score": _fmt(inventory_score) or 0.0,
                "reason": f"{inventory_score:.1f}점" if inventory_score is not None else "데이터 없음",
            },
            {
                "name": "가동률",
                "score": _fmt(operation_score) or 0.0,
                "reason": f"{operation_score:.1f}점" if operation_score is not None else "데이터 없음",
            },
        ],
        "ai_report": report["reason"] + " " + report["recommendation"],
    }
