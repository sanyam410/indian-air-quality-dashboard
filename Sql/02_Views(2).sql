USE air_quality;

CREATE OR REPLACE VIEW monthly_trend AS
SELECT
    city,
    parameter,
    DATE_FORMAT(date, '%Y-%m') AS month,
    ROUND(AVG(avg_value), 2) AS monthly_avg,
    ROUND(MAX(avg_value), 2) AS monthly_worst,
    SUM(breaches_who_limit) AS days_breached_who,
    COUNT(*) AS days_in_month
FROM city_daily_aqi
GROUP BY city, parameter, DATE_FORMAT(date, '%Y-%m')
ORDER BY city, parameter, month;

select * from monthly_trend where city='delhi' and parameter='pm25' order by month;

CREATE OR REPLACE VIEW weekday_pattern AS
SELECT
    city,
    parameter,
    DAYNAME(date) AS day_of_week,
    CASE WHEN DAYOFWEEK(date) IN (1, 7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(avg_value), 2) AS avg_value
FROM city_daily_aqi
GROUP BY city, parameter, DAYNAME(date), day_type;

select * from weekday_pattern where city='delhi' and parameter='no2' 
ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');

CREATE OR REPLACE VIEW city_overall_ranking AS
SELECT
    city,
    ROUND(AVG(times_who_limit), 2) AS avg_times_who_limit,
    ROUND(AVG(breaches_who_limit) * 100, 1) AS pct_days_any_breach,
    COUNT(DISTINCT parameter) AS pollutants_tracked
FROM city_daily_aqi
GROUP BY city
ORDER BY avg_times_who_limit DESC;

select * from city_overall_ranking;
