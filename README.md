# Indian Urban Air Quality Intelligence Dashboard

## Business Problem

Air pollution is one of India's most severe public health crises, but raw sensor readings from monitoring stations do not directly tell citizens, journalists, or policymakers how dangerous the air actually is.

Stakeholders need to understand:
- Which cities have the most dangerous air quality right now?
- How far do pollution levels exceed WHO and Indian (CPCB) safety standards?
- Is air quality improving or worsening over time?
- Are specific pollution sources (e.g. traffic) driving the problem?

This project builds an end-to-end air quality analytics pipeline using live OpenAQ sensor data, MySQL, and Power BI to transform raw multi-city sensor readings into an interactive public-health intelligence dashboard.

---

## Project Architecture

The project follows a layered pipeline architecture:

1. **Ingestion Layer** – Python script pulls daily-averaged pollutant readings from the OpenAQ v3 API across 5 cities and 111 monitoring stations
2. **Storage Layer** – Normalized MySQL schema (locations, measurements, thresholds)
3. **Aggregation Layer** – SQL views computing city-level daily averages with data-quality filtering
4. **Analytics Layer** – SQL views for AQI categorization, trend analysis, and cross-city ranking
5. **Presentation Layer** – 4-page interactive Power BI dashboard

---

## Database Layers

### Core Tables
- `locations` — 111 monitoring stations across 5 cities
- `measurements` — 102,657 daily pollutant readings, foreign-keyed to locations
- `pollutant_thresholds` — WHO 2021 and CPCB safe-limit reference values

### Aggregation Views
- `city_daily_avg` — city-level daily average per pollutant, with sensor-outlier filtering applied
- `city_daily_aqi` — adds AQI category (CPCB tiers) and WHO-limit breach flags

### Analytics Views
- `city_summary_stats` — 6-month rollup per city/pollutant (mean, worst day, % days breached)
- `monthly_trend` — monthly time-series for seasonal pattern analysis
- `weekday_pattern` — weekday vs. weekend comparison by pollutant
- `city_overall_ranking` — cross-pollutant combined severity ranking

---

## Key Metrics

Metrics are calculated using SQL aggregations against WHO and CPCB reference standards:

- **Times WHO Limit** = City's average pollutant level ÷ WHO safe limit
- **% Days Breached** = Share of days a city's readings exceeded the WHO limit
- **AQI Category** = 6-tier severity classification (Good → Severe) based on CPCB thresholds
- **Monthly Trend** = Month-over-month average, tracking seasonal change

---

## Key Findings

- **Delhi is in a severity tier of its own** — averaging 1.62x WHO limits with 46.1% of city-days breaching at least one pollutant threshold, compared to 0.76–0.89x across Mumbai, Bengaluru, Pune, and Hyderabad
- **Strong seasonal decline** in Delhi's PM2.5 — from ~98 µg/m³ in February to ~31 µg/m³ by August, consistent with winter inversion and stubble-burning season easing into monsoon
- **No significant weekday/weekend NO2 variation** in Delhi (32–36 µg/m³ range across all 7 days) — a genuine null finding suggesting NO2 sources aren't purely commuter-traffic-driven
- **Even Delhi's "best" month never reached safe levels** — every single month in the dataset breached WHO limits on 100% of days

---

## Data Quality

A sensor malfunction was identified at the Bandra Kurla Complex, Mumbai station, reporting PM2.5 values exceeding 57,000 µg/m³ on specific dates — roughly 500x neighboring stations' readings on the same day. Diagnosed via cross-station SQL comparison (`sql/03_validation.sql`) and resolved with per-pollutant sanity-cap filters applied upstream in the aggregation layer, so every downstream view inherits verified sensor data automatically.

---

## Tech Stack

- Python (pandas, requests) — API ingestion, retry/backoff, incremental-pull logic
- MySQL — relational schema design, layered SQL views, window-free aggregations
- Power BI — interactive multi-page dashboard, dynamic measures (LOOKUPVALUE), drill-down
- OpenAQ v3 API — live public sensor data

---

## Dashboard Preview

### Overview
![Overview](overview.png)

### City Detail
![City Detail](city_detail.png)

### Pollutant Comparison
![Pollutant Comparison](pollutant_comparison.png)

### Methodology & Data Quality
![Methodology](methodology.png)

