from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_latest_oil_price(db: Session) -> Optional[dict]:
    rows = db.execute(text("""
        SELECT observation_date, poildubusdm
        FROM crude_oil_prices
        WHERE poildubusdm IS NOT NULL
        ORDER BY observation_date DESC
        LIMIT 2
    """)).mappings().all()

    if not rows:
        return None

    latest = rows[0]
    price = float(latest["poildubusdm"])

    change_rate = None
    if len(rows) == 2:
        prev_price = float(rows[1]["poildubusdm"])
        if prev_price != 0:
            change_rate = round(((price - prev_price) / prev_price) * 100, 2)

    return {
        "observation_date": latest["observation_date"],
        "price": round(price, 2),
        "change_rate": change_rate,
    }


def get_oil_price_history(db: Session, months: int = 12) -> list[dict]:
    rows = db.execute(text("""
        SELECT observation_date, poildubusdm
        FROM crude_oil_prices
        WHERE poildubusdm IS NOT NULL
        ORDER BY observation_date DESC
        LIMIT :months
    """), {"months": months}).mappings().all()

    return [
        {
            "observation_date": row["observation_date"],
            "price": round(float(row["poildubusdm"]), 2),
        }
        for row in reversed(rows)
    ]
