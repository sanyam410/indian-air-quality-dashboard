import os
import requests
import json
from collections import defaultdict

API_KEY = os.environ["OPENAQ_API_KEY"]
BASE_URL = "https://api.openaq.org/v3"
headers = {"X-API-Key": API_KEY}

params = {"iso": "IN", "limit": 1000}
response = requests.get(f"{BASE_URL}/locations", headers=headers, params=params)
response.raise_for_status()
data = response.json()

locations = data["results"]
print(f"Total locations found in India: {len(locations)}")

import re

def extract_city(loc):
    locality = loc.get("locality")
    if locality:
        return locality
    name = loc.get("name", "Unknown")
    # station names follow pattern "Station, City - Agency"
    match = re.search(r",\s*([^-,]+?)\s*-", name)
    if match:
        return match.group(1).strip()
    return name  # fallback if pattern doesn't match

city_summary = defaultdict(list)

for loc in locations:
    city = extract_city(loc)
    last_updated = (loc.get("datetimeLast") or {}).get("utc", "N/A")
    sensors = [s["parameter"]["name"] for s in loc.get("sensors", [])]
    city_summary[city].append({
        "id": loc["id"],
        "last_updated": last_updated,
        "sensors": sensors,
    })

for city, locs in sorted(city_summary.items(), key=lambda x: -len(x[1]))[:15]:
    all_sensors = set()
    for l in locs:
        all_sensors.update(l["sensors"])
    print(f"{city}: {len(locs)} station(s) | parameters tracked: {sorted(all_sensors)}")

os.makedirs("data/raw", exist_ok=True)

with open("data/raw/india_locations.json", "w") as f:
    json.dump(locations, f, indent=2)

print("Saved.")

import os
import requests
import time
import json
from datetime import datetime, timedelta

API_KEY = os.environ["OPENAQ_API_KEY"] 
BASE_URL = "https://api.openaq.org/v3"
headers = {"X-API-Key": API_KEY}

date_to = datetime.utcnow().date()
date_from = date_to - timedelta(days=180)


all_locations = locations

delhi_locations = [
    loc for loc in all_locations
    if "delhi" in (loc.get("name", "") + str(loc.get("locality", ""))).lower()
]
print(f"Delhi stations to process: {len(delhi_locations)}")

all_daily_records = []

for loc in delhi_locations[:3]:  
    loc_id = loc["id"]
    sensors_resp = requests.get(f"{BASE_URL}/locations/{loc_id}/sensors", headers=headers)
    sensors_resp.raise_for_status()
    sensors = sensors_resp.json()["results"]
    time.sleep(0.5)  # be polite to the API

    for sensor in sensors:
        sensor_id = sensor["id"]
        param = sensor["parameter"]["name"]

        days_resp = requests.get(
            f"{BASE_URL}/sensors/{sensor_id}/days",
            headers=headers,
            params={"date_from": str(date_from), "date_to": str(date_to), "limit": 200}
        )
        if days_resp.status_code != 200:
            print(f"  Skipped sensor {sensor_id} ({param}) — status {days_resp.status_code}")
            continue

        results = days_resp.json()["results"]
        for r in results:
            all_daily_records.append({
                "location_id": loc_id,
                "location_name": loc["name"],
                "parameter": param,
                "date": r["period"]["datetimeFrom"]["local"][:10],
                "value": r["value"],
                "unit": sensor["parameter"]["units"],
            })
        time.sleep(0.5)

print(f"Total daily records pulled: {len(all_daily_records)}")

print(all_daily_records[:5])