import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

RAW_FILE = "한국산업단지공단_국가산업단지 산업동향정보_20260331.xlsx"
OUTPUT_FILE = "industry_trend_clean.csv"


def read_sheet(sheet_name: str, columns: list[str]) -> pd.DataFrame:
    df = pd.read_excel(
        RAW_DIR / RAW_FILE,
        sheet_name=sheet_name,
        header=None,
        skiprows=3
    )

    df = df.iloc[:, :len(columns)]
    df.columns = columns

    df = df.dropna(subset=["complex_name"])
    df["complex_name"] = df["complex_name"].astype(str).str.strip()
    df = df[df["complex_name"] != ""]

    return df


resident = read_sheet("표1 단지별 입주", [
    "complex_name",
    "complex_type",
    "resident_current",
    "resident_previous",
    "active_current",
    "active_previous",
    "rental_companies",
])

production = read_sheet("표4 단지별 생산", [
    "complex_name",
    "complex_type",
    "production_current",
    "production_previous",
    "production_cumulative",
    "production_change_rate",
])

export = read_sheet("표6 단지별 수출", [
    "complex_name",
    "complex_type",
    "export_current",
    "export_previous",
    "export_cumulative",
    "export_change_rate",
])

operation = pd.read_excel(
    RAW_DIR / RAW_FILE,
    sheet_name="표10 단지별 가동률",
    header=None,
    skiprows=3
)

operation = operation.iloc[:, :8]
operation.columns = [
    "complex_name",
    "complex_type",
    "manufacturing_active_companies",
    "max_production_capacity",
    "quarter_production_amount",
    "operation_rate_current",
    "operation_rate_previous",
    "operation_rate_change",
]

operation = operation.dropna(subset=["complex_name"])
operation["complex_name"] = operation["complex_name"].astype(str).str.strip()
operation = operation[operation["complex_name"] != ""]

df = resident.merge(
    production[[
        "complex_name",
        "complex_type",
        "production_current",
        "production_change_rate",
    ]],
    on=["complex_name", "complex_type"],
    how="left"
)

df = df.merge(
    export[[
        "complex_name",
        "complex_type",
        "export_current",
        "export_change_rate",
    ]],
    on=["complex_name", "complex_type"],
    how="left"
)

df = df.merge(
    operation[[
        "complex_name",
        "complex_type",
        "operation_rate_current",
    ]],
    on=["complex_name", "complex_type"],
    how="left"
)

df = df[[
    "complex_name",
    "complex_type",
    "resident_current",
    "active_current",
    "production_current",
    "production_change_rate",
    "export_current",
    "export_change_rate",
    "operation_rate_current",
]]

numeric_cols = [
    "resident_current",
    "active_current",
    "production_current",
    "production_change_rate",
    "export_current",
    "export_change_rate",
    "operation_rate_current",
]

for col in numeric_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.drop_duplicates()

df.to_csv(
    PROCESSED_DIR / OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 50)
print("산업동향 데이터 전처리 완료")
print("=" * 50)
print(df.head())
print("\n데이터 개수 :", len(df))
print("컬럼 수 :", len(df.columns))
print("중복 단지명 :", df["complex_name"].duplicated().sum())
print("\n컬럼 목록")
print(df.columns.tolist())
print("\n저장 완료")
print(PROCESSED_DIR / OUTPUT_FILE)