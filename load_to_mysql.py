import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus


load_dotenv()

USER = os.environ["MYSQL_USER"]
PASSWORD = os.environ["MYSQL_PASSWORD"]
HOST = os.environ.get("MYSQL_HOST", "localhost")
DB = os.environ["MYSQL_DB"]

engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}")
# 1. Load the raw CSV
df = pd.read_csv("data/raw/air_quality_daily.csv")
print(f"Loaded {len(df)} rows from CSV")

# 2. Build the locations table (one row per unique station)
locations_df = (
    df[["location_id", "location_name", "city"]]
    .drop_duplicates(subset="location_id")
    .reset_index(drop=True)
)
print(f"Unique locations: {len(locations_df)}")

measurements_df = df[["location_id", "parameter", "date", "value", "unit"]].copy()

# 4. Insert locations FIRST — measurements has a foreign key pointing to it,
#    so locations must exist before measurements can reference them
locations_df.to_sql(
    "locations",
    con=engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=500,
)
print("Locations inserted.")

measurements_df.to_sql(
    "measurements",
    con=engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=2000,
)
print("Measurements inserted.")

with engine.connect() as conn:
    loc_count = conn.execute(text("SELECT COUNT(*) FROM locations")).scalar()
    meas_count = conn.execute(text("SELECT COUNT(*) FROM measurements")).scalar()
    print(f"DB check — locations: {loc_count}, measurements: {meas_count}")

