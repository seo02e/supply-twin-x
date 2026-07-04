import os
import re
from pathlib import Path

import pandas as pd
import requests
import xmltodict
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.models import CustomsTrade, Inventory

load_dotenv()

CUSTOMS_API_KEY = os.getenv("CUSTOMS_API_KEY")
CUSTOMS_BASE_URL = "https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList"

BACKEND_DIR = Path(__file__).resolve().parents[2]
HSCODE_CSV_PATH = BACKEND_DIR / "data" / "processed" / "hscode_clean.csv"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", str(value or "").strip())


def to_float(value):
    try:
        if value in (None, "", "-"):
            return None
        return float(value)
    except Exception:
        return None


def find_hs_code(material_name: str, current_hs_code: str | None = None) -> str | None:
    if not HSCODE_CSV_PATH.exists():
        raise FileNotFoundError(f"HS CODE CSV 파일이 없습니다: {HSCODE_CSV_PATH}")

    df = pd.read_csv(HSCODE_CSV_PATH, dtype=str)
    df["hs_code"] = df["hs_code"].astype(str).str.strip()
    df["item_name"] = df["item_name"].astype(str).str.strip()

    # 1순위: inventories.hs_code가 2709, 7502처럼 앞자리 코드면
    # hscode_clean.csv에서 해당 코드로 시작하는 10자리 코드 찾기
    if current_hs_code:
        prefix = str(current_hs_code).strip()

        matched = df[
            df["hs_code"].str.startswith(prefix)
            & (df["hs_code"].str.len() >= 10)
        ].copy()

        if not matched.empty:
            matched["name_len"] = matched["item_name"].str.len()
            matched = matched.sort_values(["name_len", "hs_code"])
            return str(matched.iloc[0]["hs_code"])

    # 2순위: material_name이 품목명에 포함되는 것 찾기
    target = normalize_text(material_name)

    matched = df[
        df["item_name"].apply(lambda x: target in normalize_text(x))
        & (df["hs_code"].str.len() >= 10)
    ].copy()

    if not matched.empty:
        matched["name_len"] = matched["item_name"].str.len()
        matched = matched.sort_values(["name_len", "hs_code"])
        return str(matched.iloc[0]["hs_code"])

    return None


def fetch_customs_api(strtYymm: int, endYymm: int, hs_code: str):
    if not CUSTOMS_API_KEY:
        raise Exception("CUSTOMS_API_KEY가 .env 또는 Railway Variables에 없습니다.")

    params = {
        "serviceKey": CUSTOMS_API_KEY,
        "strtYymm": strtYymm,
        "endYymm": endYymm,
        "hsSgn": hs_code,
    }

    response = requests.get(CUSTOMS_BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Customs API error: {response.status_code}")

    data = xmltodict.parse(response.text)

    header = data.get("response", {}).get("header", {})
    if header.get("resultCode") != "00":
        raise Exception(f"Customs API result error: {header}")

    items = (
        data.get("response", {})
        .get("body", {})
        .get("items", {})
        .get("item", [])
    )

    if isinstance(items, dict):
        items = [items]

    return items


def get_customs_import_export(
    db: Session,
    company_id: int,
    strtYymm: int,
    endYymm: int,
):
    inventories = (
        db.query(Inventory)
        .filter(Inventory.company_id == company_id)
        .all()
    )

    if not inventories:
        raise Exception(f"company_id={company_id}의 재고 데이터가 없습니다.")

    saved_count = 0
    results = []

    for inventory in inventories:
        material_name = inventory.material_name

        if not material_name:
            continue

        hs_code = find_hs_code(
            material_name=material_name,
            current_hs_code=inventory.hs_code,
        )

        if not hs_code:
            results.append({
                "material_name": material_name,
                "input_hs_code": inventory.hs_code,
                "status": "HS_CODE_NOT_FOUND",
                "message": "HS CODE를 찾지 못했습니다."
            })
            continue

        # 기존 4자리 코드를 10자리 코드로 업데이트
        inventory.hs_code = hs_code

        items = fetch_customs_api(strtYymm, endYymm, hs_code)

        item_saved_count = 0

        for item in items:
            if item.get("year") == "총계":
                continue

            trade = CustomsTrade(
                company_id=company_id,
                hs_code=item.get("hsCode") or hs_code,
                item_name=item.get("statKor") or material_name,
                country_name=None,
                import_amount=to_float(item.get("impDlr")),
                import_weight=to_float(item.get("impWgt")),
                export_amount=to_float(item.get("expDlr")),
                export_weight=to_float(item.get("expWgt")),
                trade_month=item.get("year"),
            )

            db.add(trade)
            saved_count += 1
            item_saved_count += 1

        results.append({
            "material_name": material_name,
            "resolved_hs_code": hs_code,
            "status": "SAVED",
            "saved_count": item_saved_count
        })

    db.commit()

    return {
        "company_id": company_id,
        "saved_count": saved_count,
        "results": results
    }