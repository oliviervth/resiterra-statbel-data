import json
import requests
from pathlib import Path

EXPORT_URL = "https://bestat.statbel.fgov.be/bestat/api/views/b7c7f4b0-d476-4446-8c91-ba0112ea3ac0/result/JSON"

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "kadaster_bodembezetting.json"

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
