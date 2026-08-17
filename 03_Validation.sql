-- ============================================
-- Validation: data coverage checks and outlier investigation
-- ============================================

USE air_quality;

-- Coverage check: how many days of data per city/pollutant (out of ~180)
SELECT 
    l.city,
    m.parameter,
    COUNT(DISTINCT m.date) AS days_with_data,
    MIN(m.date) AS earliest_date,
    MAX(m.date) AS latest_date
FROM measurements m
JOIN locations l ON m.location_id = l.location_id
GROUP BY l.city, m.parameter
ORDER BY l.city, m.parameter;

-- Outlier investigation: Mumbai PM2.5 sensor malfunction (2026-05-01/02/08)
-- Confirmed by comparing all stations on the same day — only one or two
-- stations spiked while the rest reported normal values.
SELECT 
    l.location_name,
    m.date,
    m.value
FROM measurements m
JOIN locations l ON m.location_id = l.location_id
WHERE l.city = 'Mumbai' 
  AND m.parameter = 'pm25'
  AND m.date IN ('2026-05-01', '2026-05-02', '2026-05-08')
ORDER BY m.date, m.value DESC;