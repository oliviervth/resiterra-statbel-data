import json
import requests
from pathlib import Path

EXPORT_URL = "https://bestat.statbel.fgov.be/bestat/api/views/5ff707d8-0bde-42c4-9d56-52a095a94778/result/JSON"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "income.json"

def download():
    print("Downloading Statbel income data...")
  
    response = requests.get(EXPORT_URL, timeout=120)
    response.raise_for_status()

    data = response.json()

    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
        download()
