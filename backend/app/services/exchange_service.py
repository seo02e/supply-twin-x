import os
import requests
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()


def parse_rate(value):
    if value is None:
        return None
    return float(str(value).replace(",", "").strip())


def fetch_and_save_usd_krw(db: Session, search_date: str | None = None):
    api_key = os.getenv("EXCHANGE_API_KEY")
    api_url = os.getenv(
        "EXCHANGE_API_URL",
        "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
    )

    if not api_key:
        raise Exception("EXCHANGE_API_KEY가 .env에 없습니다.")

    if search_date is None:
        search_date = datetime.now().strftime("%Y%m%d")

    params = {
        "authkey": api_key,
        "searchdate": search_date,
        "data": "AP01"
    }

    response = requests.get(api_url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    usd_item = None
    for item in data:
        if item.get("cur_unit") == "USD":
            usd_item = item
            break

    if not usd_item:
        raise Exception("USD 환율 데이터를 찾지 못했습니다.")

    base_rate = parse_rate(usd_item.get("deal_bas_r"))
    rate_date = datetime.strptime(search_date, "%Y%m%d").date()

    db.execute(text("""
        DELETE FROM exchange_rates
        WHERE currency_code = 'USD'
        AND rate_date = :rate_date
    """), {"rate_date": rate_date})

    db.execute(text("""
        INSERT INTO exchange_rates (
            currency_code,
            currency_name,
            base_rate,
            rate_date
        )
        VALUES (
            :currency_code,
            :currency_name,
            :base_rate,
            :rate_date
        )
    """), {
        "currency_code": "USD",
        "currency_name": usd_item.get("cur_nm"),
        "base_rate": base_rate,
        "rate_date": rate_date
    })

    db.commit()

    return {
        "currency_code": "USD",
        "currency_name": usd_item.get("cur_nm"),
        "base_rate": base_rate,
        "rate_date": rate_date
    }


def get_latest_usd_krw(db: Session):
    row = db.execute(text("""
        SELECT currency_code, currency_name, base_rate, rate_date
        FROM exchange_rates
        WHERE currency_code = 'USD'
        ORDER BY rate_date DESC
        LIMIT 1
    """)).mappings().first()

    if not row:
        return None

    return dict(row)