import json
import re
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/bouwvergunningen.xlsx")
OUTPUT_DIR = Path("data/bouwvergunningen")

def safe_filename(name):
    name = str(name).strip().upper()
    name = re.sub(r"[^A-Z0-9_-]+", "_", name)
    return name

def main():
    print("Reading bouwvergunningen.xlsx...")

    df = pd.read_excel(
        INPUT_FILE,
        engine="openpyxl",
        dtype=str
    )

    print(f"Rows loaded: {len(df)}")

    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")

    # Enkel gemeenteniveau behouden
    df = df[df["CD_REFNIS_LEVEL"].astype(str) == "5"]

    print(f"Municipality rows: {len(df)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    grouped = df.groupby("REFNIS_NL")

    for gemeente, group in grouped:
        filename = safe_filename(gemeente) + ".json"
        output_file = OUTPUT_DIR / filename

        records = group.where(pd.notnull(group), None).to_dict(orient="records")

        output = {
            "dataset": "bouwvergunningen",
            "gemeente": gemeente,
            "record_count": len(records),
            "facts": records
        }

        output_file.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Saved {output_file}")

    print("Done.")

if __name__ == "__main__":
    main()
