from sqlalchemy.orm import Session
from sqlalchemy import text


def calculate_risk_summary(db: Session, company_id: int = 1):
    # ==========================
    # 1. 최근 원유 가격 변동률
    # ==========================
    latest_oil = db.execute(text("""
        SELECT observation_date, poildubusdm
        FROM crude_oil_prices
        WHERE poildubusdm IS NOT NULL
        ORDER BY observation_date DESC
        LIMIT 1
    """)).mappings().first()

    prev_oil = db.execute(text("""
        SELECT observation_date, poildubusdm
        FROM crude_oil_prices
        WHERE poildubusdm IS NOT NULL
        ORDER BY observation_date DESC
        OFFSET 3 LIMIT 1
    """)).mappings().first()

    oil_change_rate = 0

    if latest_oil and prev_oil:
        latest_price = float(latest_oil["poildubusdm"])
        prev_price = float(prev_oil["poildubusdm"])

        if prev_price != 0:
            oil_change_rate = ((latest_price - prev_price) / prev_price) * 100

    oil_score = min(30, max(0, oil_change_rate * 2))

    # ==========================
    # 2. 재고 위험
    # ==========================
    materials = db.execute(text("""
        SELECT
            material_name,
            current_stock,
            safety_stock
        FROM inventories
        WHERE company_id = :company_id
    """), {
        "company_id": company_id
    }).mappings().all()

    shortage_count = 0
    inventory_score = 0

    for item in materials:

        current_stock = float(item["current_stock"] or 0)
        safety_stock = float(item["safety_stock"] or 0)

        if current_stock < safety_stock:
            shortage_count += 1
            inventory_score += 20

    inventory_score = min(35, inventory_score)

    # ==========================
    # 3. 산업단지 가동률
    # ==========================
    industry = db.execute(text("""
        SELECT
            operation_rate_current,
            production_change_rate,
            export_change_rate
        FROM industry_trends
        WHERE operation_rate_current IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
    """)).mappings().first()

    industry_score = 0

    if industry:

        operation_rate = float(industry["operation_rate_current"] or 0)
        production_change = float(industry["production_change_rate"] or 0)

        if operation_rate < 80:
            industry_score += 15

        if production_change < 0:
            industry_score += 10

    industry_score = min(25, industry_score)

    # ==========================
    # 4. 총 위험도
    # ==========================
    total_score = oil_score + inventory_score + industry_score
    total_score = min(100, total_score)

    if total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ==========================
    # 5. AI 리포트
    # ==========================
    ai_report = (
        f"최근 국제 원유 가격은 {oil_change_rate:.2f}% 변동하였습니다. "
        f"현재 안전재고 이하 원자재는 {shortage_count}개입니다. "
        f"산업단지 생산지표를 함께 분석한 결과 현재 공급망 위험도는 "
        f"{risk_level} 단계({total_score:.1f}점)입니다. "
        f"재고 부족 품목은 우선 발주를 검토하고, 원유 가격 상승이 지속될 경우 "
        f"추가 구매 및 대체 공급처 확보를 권장합니다."
    )

    return {
        "total_score": round(total_score, 2),
        "risk_level": risk_level,
        "oil_score": round(oil_score, 2),
        "inventory_score": round(inventory_score, 2),
        "industry_score": round(industry_score, 2),
        "factors": [
            {
                "name": "원유 가격",
                "score": round(oil_score, 2),
                "reason": f"최근 원유 가격 변동률 {oil_change_rate:.2f}%"
            },
            {
                "name": "재고",
                "score": round(inventory_score, 2),
                "reason": f"안전재고 이하 품목 {shortage_count}개"
            },
            {
                "name": "산업동향",
                "score": round(industry_score, 2),
                "reason": "산업단지 가동률 및 생산 증감률 반영"
            }
        ],
        "ai_report": ai_report
    }