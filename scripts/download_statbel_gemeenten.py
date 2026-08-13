import json
import re
from pathlib import Path

import pandas as pd
import requests

SOURCE_URL = "https://statbel.fgov.be/sites/default/files/files/opendata/REFNIS%20code/TU_COM_REFNIS.xlsx"
INPUT_FILE = Path("data/refnis.xlsx")
OUTPUT_FILE = Path("data/gemeenten.json")


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_code(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    if len(digits) <= 5:
        return digits.zfill(5)
    return digits


def download_refnis_if_needed():
    INPUT_FILE.parent.mkdir(exist_ok=True)
    if INPUT_FILE.exists() and INPUT_FILE.stat().st_size > 1000:
        print(f"Using existing {INPUT_FILE}")
        return

    print("Downloading official Statbel REFNIS XLSX...")
    response = requests.get(SOURCE_URL, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    INPUT_FILE.write_bytes(response.content)
    print(f"Saved source file to {INPUT_FILE}")


def choose_column(columns, candidates):
    normalized = {str(c).lower().strip(): c for c in columns}
    for candidate in candidates:
        for key, original in normalized.items():
            if candidate in key:
                return original
    return None


def read_refnis():
    sheets = pd.read_excel(INPUT_FILE, sheet_name=None, dtype=str, engine="openpyxl")

    best_df = None
    best_score = -1

    for sheet_name, df in sheets.items():
        df = df.dropna(how="all")
        cols = list(df.columns)
        code_col = choose_column(cols, ["refnis", "nis", "code"])
        name_col = choose_column(cols, ["naam", "name", "nom"])        
        score = 0
        if code_col is not None:
            score += 2
        if name_col is not None:
            score += 2
        score += min(len(df), 1000) / 1000
        if score > best_score:
            best_score = score
            best_df = df.copy()

    if best_df is None:
        raise ValueError("Could not read any usable worksheet from refnis.xlsx")

    cols = list(best_df.columns)
    code_col = choose_column(cols, ["refnis", "nis", "code"])
    name_nl_col = choose_column(cols, ["naam", "name", "nom"])
    province_col = choose_column(cols, ["province", "provincie"])
    arrondissement_col = choose_column(cols, ["arrondissement"])
    region_col = choose_column(cols, ["gewest", "region", "région"])
    level_col = choose_column(cols, ["niveau", "level", "type"])

    if code_col is None or name_nl_col is None:
        raise ValueError(f"Could not identify code/name columns. Columns found: {cols}")

    records = []
    for _, row in best_df.iterrows():
        nis = normalize_code(row.get(code_col))
        name = normalize_text(row.get(name_nl_col))

        if not re.fullmatch(r"\d{5}", nis):
            continue
        if not name:
            continue

        level = normalize_text(row.get(level_col)).lower() if level_col else ""

        is_municipality = False
        if level:
            is_municipality = any(x in level for x in ["gemeente", "municip", "commune"])
        else:
            # Fallback: municipalities normally do not use the 000 ending used by higher levels.
            is_municipality = not nis.endswith("000")

        if not is_municipality:
            continue

        records.append({
            "nis": nis,
            "gemeente": name,
            "arrondissement": normalize_text(row.get(arrondissement_col)) if arrondissement_col else "",
            "provincie": normalize_text(row.get(province_col)) if province_col else "",
            "gewest": normalize_text(row.get(region_col)) if region_col else ""
        })

    # Deduplicate by NIS code and sort.
    unique = {record["nis"]: record for record in records}
    gemeenten = sorted(unique.values(), key=lambda x: x["nis"])
    return gemeenten


def main():
    download_refnis_if_needed()
    gemeenten = read_refnis()

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    output = {
        "source": "Statbel REFNIS code",
        "source_url": SOURCE_URL,
        "description": "Gemeentenlijst met NIS-code voor koppeling van Resiterra Statbel datasets.",
        "count": len(gemeenten),
        "gemeenten": gemeenten
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(gemeenten)} municipalities to {OUTPUT_FILE}")
    if len(gemeenten) < 500:
        print("WARNING: municipality count is unexpectedly low. Check refnis.xlsx structure.")


if __name__ == "__main__":
    main()
