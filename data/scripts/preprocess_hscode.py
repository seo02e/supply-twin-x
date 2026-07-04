from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = RAW_DIR / "HSCODE.xlsx"
OUTPUT_FILE = PROCESSED_DIR / "hscode_clean.csv"


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 엑셀의 4번째 줄이 실제 컬럼명: 품목코드 / 품목명
    df = pd.read_excel(INPUT_FILE, header=3)

    df.columns = [str(col).strip() for col in df.columns]

    clean_df = df[["품목코드", "품목명"]].copy()
    clean_df.columns = ["hs_code", "item_name"]

    clean_df["hs_code"] = clean_df["hs_code"].astype(str).str.replace(".0", "", regex=False).str.strip()
    clean_df["item_name"] = clean_df["item_name"].astype(str).str.strip()

    clean_df = clean_df[
        (clean_df["hs_code"] != "")
        & (clean_df["hs_code"] != "nan")
        & (clean_df["item_name"] != "")
        & (clean_df["item_name"] != "nan")
    ]

    clean_df = clean_df.drop_duplicates(subset=["hs_code"])

    clean_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"완료: {OUTPUT_FILE}")
    print(f"총 {len(clean_df)}건 저장")
    print(clean_df.head(20))


if __name__ == "__main__":
    main()