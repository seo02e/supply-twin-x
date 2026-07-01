import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

RAW_FILE = "조달청_홈페이지_비축물자_원자재_일일가격_20250926.csv"

# CSV 읽기
df = pd.read_csv(
    RAW_DIR / RAW_FILE,
    encoding="cp949"
)

# 필요한 컬럼만 선택 및 이름 변경
df = df.rename(columns={
    "물품명": "material_name",
    "판매지방청명": "sales_office",
    "판매금액": "price",
    "판매종료일자": "price_date",
})

df = df[
    [
        "material_name",
        "sales_office",
        "price",
        "price_date",
    ]
]

# 데이터 타입 변환
df["price"] = (
    df["price"]
    .astype(str)
    .str.replace(",", "", regex=False)
)

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df["price_date"] = pd.to_datetime(
    df["price_date"],
    errors="coerce"
)

# 결측 제거
df = df.dropna(
    subset=[
        "material_name",
        "price",
        "price_date",
    ]
)

# 중복 제거
df = df.drop_duplicates()

# 저장
df.to_csv(
    PROCESSED_DIR / "material_price_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("=" * 50)
print("원자재 가격 데이터 전처리 완료")
print("=" * 50)

print(df.head())

print("\n데이터 개수 :", len(df))
print("컬럼 수 :", len(df.columns))
print("중복 :", df.duplicated().sum())

print("\n컬럼 목록")
print(df.columns.tolist())

print("\n저장 완료")
print(PROCESSED_DIR / "material_price_clean.csv")