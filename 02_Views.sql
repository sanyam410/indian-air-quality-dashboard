-- ============================================
-- Views: daily aggregation, AQI categorization, city summary
-- ============================================

USE air_quality;

-- City-level daily average per pollutant, across all reporting stations.
-- Filters out implausible sensor readings (see sql/03_validation.sql for
-- the investigation: a faulty station at Bandra Kurla Complex, Mumbai
-- reported PM2.5 values of 57,300+ µg/m³ on 2026-05-01/02 while every
-- other station in the city that day read normally — confirmed sensor
-- malfunction, not a real event, via cross-station comparison).
CREATE OR REPLACE VIEW city_daily_avg AS
SELECT 
    l.city,
    m.parameter,
    m.date,
    ROUND(AVG(m.value), 2) AS avg_value,
    COUNT(DISTINCT m.location_id) AS stations_reporting
FROM measurements m
JOIN locations l ON m.location_id = l.location_id
WHERE 
    (m.parameter = 'pm25' AND m.value <= 1000)
    OR (m.parameter = 'pm10' AND m.value <= 1000)
    OR (m.parameter = 'no2'  AND m.value <= 1000)
    OR (m.parameter = 'so2'  AND m.value <= 2000)
    OR (m.parameter = 'co'   AND m.value <= 30000)
    OR (m.parameter = 'o3'   AND m.value <= 500)
GROUP BY l.city, m.parameter, m.date;

-- Adds AQI category (CPCB-based tiers) and WHO-limit comparison on top
-- of the clean daily averages.
CREATE OR REPLACE VIEW city_daily_aqi AS
SELECT 
    c.city,
    c.parameter,
    c.date,
    c.avg_value,
    c.stations_reporting,
    t.who_limit,
    t.cpcb_limit,
    ROUND(c.avg_value / t.who_limit, 2) AS times_who_limit,
    CASE 
        WHEN c.avg_value <= t.cpcb_limit * 0.5 THEN 'Good'
        WHEN c.avg_value <= t.cpcb_limit THEN 'Satisfactory'
        WHEN c.avg_value <= t.cpcb_limit * 1.5 THEN 'Moderate'
        WHEN c.avg_value <= t.cpcb_limit * 2 THEN 'Poor'
        WHEN c.avg_value <= t.cpcb_limit * 3 THEN 'Very Poor'
        ELSE 'Severe'
    END AS aqi_category,
    CASE
        WHEN c.avg_value > t.who_limit THEN 1
        ELSE 0
    END AS breaches_who_limit
FROM city_daily_avg c
JOIN pollutant_thresholds t ON c.parameter = t.parameter;

-- 6-month summary per city/pollutant — mean, worst day, % of days
-- breaching WHO limits. Powers the city-comparison chart.
CREATE OR REPLACE VIEW city_summary_stats AS
SELECT 
    city,
    parameter,
    ROUND(AVG(avg_value), 2) AS mean_value,
    ROUND(MAX(avg_value), 2) AS worst_day_value,
    SUM(breaches_who_limit) AS days_breached_who,
    COUNT(*) AS total_days,
    ROUND(SUM(breaches_who_limit) * 100.0 / COUNT(*), 1) AS pct_days_breached
FROM city_daily_aqi
GROUP BY city, parameter;
