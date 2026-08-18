import json
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/bouwvergunningen.xlsx")
OUTPUT_FILE = Path("data/bouwvergunningen.json")

def clean_value(value):
    if pd.isna(value):
        return None
    return value

def main():
    print("Reading bouwvergunningen.xlsx...")

    df = pd.read_excel(INPUT_FILE, engine="openpyxl", dtype=str)

    print(f"Rows loaded: {len(df)}")

    df = df.dropna(how="all")

    # Enkel gemeentelijk niveau behouden
    if "CD_REFNIS_LEVEL" in df.columns:
        df = df[df["CD_REFNIS_LEVEL"].astype(str) == "5"]

    # Kolommen opschonen
    df.columns = [str(col).strip() for col in df.columns]

    records = df.where(pd.notnull(df), None).to_dict(orient="records")

    output = {
        "source": "Statbel bouwvergunningen",
        "description": "Bouwvergunningen per gemeente, maand en type woning.",
        "record_count": len(records),
        "facts": records
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Saved {len(records)} records to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
