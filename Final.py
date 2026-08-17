import os
import re
import time
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = os.environ["OPENAQ_API_KEY"]
BASE_URL = "https://api.openaq.org/v3"
headers = {"X-API-Key": API_KEY}

CORE_PARAMS = {"pm25", "pm10", "no2", "so2", "co", "o3"}
TARGET_CITIES = ["Delhi", "New Delhi", "Mumbai", "Hyderabad", "Bengaluru", "Pune"]

date_to = datetime.utcnow().date()
date_from = date_to - timedelta(days=180)

OUTPUT_PATH = "data/raw/air_quality_daily.csv"


def extract_city(loc):
    locality = loc.get("locality")
    if locality:
        return locality
    name = loc.get("name", "Unknown")
    match = re.search(r",\s*([^-,]+?)\s*-", name)
    return match.group(1).strip() if match else name


def get_with_retry(url, params=None, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            return resp
        if resp.status_code == 429:
            wait = 2 ** attempt  # exponential backoff: 1, 2, 4, 8, 16 seconds
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        return resp  # other errors: return as-is, caller decides
    return resp


def normalize_city(city_name):
    if city_name in ("Delhi", "New Delhi"):
        return "Delhi"
    return city_name


with open("data/raw/india_locations.json") as f:
    all_locations = json.load(f)

target_locations = [
    loc for loc in all_locations
    if extract_city(loc) in TARGET_CITIES
]
print(f"Total stations to process: {len(target_locations)}")

# Resume support: skip locations already fully processed
already_done = set()
if os.path.exists(OUTPUT_PATH):
    existing = pd.read_csv(OUTPUT_PATH)
    already_done = set(existing["location_id"].unique())
    print(f"Resuming — {len(already_done)} locations already done")

write_header = not os.path.exists(OUTPUT_PATH)

for i, loc in enumerate(target_locations):
    loc_id = loc["id"]
    if loc_id in already_done:
        continue

    city = normalize_city(extract_city(loc))
    print(f"[{i+1}/{len(target_locations)}] {loc['name']} ({city})")

    sensors_resp = get_with_retry(f"{BASE_URL}/locations/{loc_id}/sensors")
    if sensors_resp.status_code != 200:
        print(f"  Failed to get sensors — status {sensors_resp.status_code}")
        continue
    sensors = sensors_resp.json()["results"]
    time.sleep(0.5)

    loc_records = []
    for sensor in sensors:
        param = sensor["parameter"]["name"]
        if param not in CORE_PARAMS:
            continue

        sensor_id = sensor["id"]
        days_resp = get_with_retry(
            f"{BASE_URL}/sensors/{sensor_id}/days",
            params={"date_from": str(date_from), "date_to": str(date_to), "limit": 200}
        )
        if days_resp.status_code != 200:
            print(f"  Skipped sensor {sensor_id} ({param}) — status {days_resp.status_code}")
            continue

        for r in days_resp.json()["results"]:
            loc_records.append({
                "location_id": loc_id,
                "location_name": loc["name"],
                "city": city,
                "parameter": param,
                "date": r["period"]["datetimeFrom"]["local"][:10],
                "value": r["value"],
                "unit": sensor["parameter"]["units"],
            })
        time.sleep(0.5)

    # checkpoint: append this location's records immediately
    if loc_records:
        df = pd.DataFrame(loc_records)
        df.to_csv(OUTPUT_PATH, mode="a", header=write_header, index=False)
        write_header = False
        print(f"  Saved {len(loc_records)} records")

print("Done.")

df = pd.read_csv("data/raw/air_quality_daily.csv")
print(df.shape)
print(df["city"].value_counts())

print(df["parameter"].value_counts())
print()
print(df.head())
