import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

# 현재 파일: backend/data/scripts/load_to_db.py
# backend 폴더를 import 경로에 추가
BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_DIR))

# app/db/database.py의 engine 사용
from backend.app.db.database import engine  # noqa: E402

PROCESSED_DIR = BACKEND_DIR / "data" / "processed"


def clear_table(table_name: str):
    with engine.begin() as conn:
        conn.execute(
            text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        )


def load_csv(file_name: str, table_name: str):
    file_path = PROCESSED_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {file_path}")

    df = pd.read_csv(file_path)

    if table_name == "crude_oil_prices":
        df = df.rename(
            columns={
                "POILDUBUSDM": "poildubusdm"
            }
        )

    clear_table(table_name)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"✅ {file_name} → {table_name} 적재 완료: {len(df)}건")


if __name__ == "__main__":
    load_csv("crude_oil_price.csv", "crude_oil_prices")
    load_csv("material_price_clean.csv", "material_prices")
    load_csv("industrial_complex_clean.csv", "industrial_complexes")
    load_csv("industry_trend_clean.csv", "industry_trends")
    load_csv("hscode_clean.csv", "hs_codes")