import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

RAW_FILE = "한국산업단지공단_전국산업단지현황통계_20250930.xlsx"

df = pd.read_excel(
    RAW_DIR / RAW_FILE,
    sheet_name="전국산업단지현황",
    header=[3, 4]
)

df = df[
    [
        ("유형", "Unnamed: 0_level_1"),
        ("시도", "Unnamed: 1_level_1"),
        ("시군", "Unnamed: 2_level_1"),
        ("단지명", "Unnamed: 3_level_1"),
        ("조성상태", "Unnamed: 4_level_1"),
        ("산업시설구역", "분양률"),
        ("입주업체", "Unnamed: 12_level_1"),
        ("가동업체", "Unnamed: 13_level_1"),
    ]
]

df.columns = [
    "complex_type",
    "province",
    "city",
    "complex_name",
    "development_status",
    "sale_rate",
    "resident_companies",
    "active_companies",
]

df = df.dropna(subset=["complex_name"])

df["complex_name"] = (
    df["complex_name"]
    .astype(str)
    .str.replace("\xa0", "", regex=False)
    .str.strip()
)

df = df[df["complex_name"] != ""]

numeric_cols = [
    "sale_rate",
    "resident_companies",
    "active_companies",
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
    PROCESSED_DIR / "industrial_complex_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head())
print(df.shape)
print("중복 단지명 :", df["complex_name"].duplicated().sum())
print("✅ industrial_complex_clean.csv 생성 완료")