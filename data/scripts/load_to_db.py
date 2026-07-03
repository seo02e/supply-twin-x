import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"

DB_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/supply_twin"
engine = create_engine(DB_URL)


def clear_table(table_name: str):
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))


def load_csv(file_name: str, table_name: str):
    file_path = PROCESSED_DIR / file_name
    df = pd.read_csv(file_path)

    # 원유 가격 CSV 컬럼명 변경
    if table_name == "crude_oil_prices":
        df = df.rename(columns={
            "observation_date": "observation_date",
            "POILDUBUSDM": "poildubusdm"
        })

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