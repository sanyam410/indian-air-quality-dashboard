-- ============================================
-- Schema: air_quality database
-- Creates locations, measurements, and pollutant_thresholds tables
-- ============================================

CREATE DATABASE IF NOT EXISTS air_quality;
USE air_quality;

CREATE TABLE locations (
    location_id INT PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    parameter VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    value DECIMAL(10, 3),
    unit VARCHAR(20),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_date (date),
    INDEX idx_parameter (parameter),
    INDEX idx_location (location_id)
);

CREATE TABLE pollutant_thresholds (
    parameter VARCHAR(20) PRIMARY KEY,
    who_limit DECIMAL(10, 3),
    cpcb_limit DECIMAL(10, 3),
    unit VARCHAR(20)
);

-- WHO 2021 guidelines + CPCB (India) standards, 24-hr averages where applicable
INSERT INTO pollutant_thresholds VALUES
('pm25', 15.0, 60.0, 'µg/m³'),
('pm10', 45.0, 100.0, 'µg/m³'),
('no2', 25.0, 80.0, 'µg/m³'),
('so2', 40.0, 80.0, 'µg/m³'),
('co', 4000.0, 4000.0, 'µg/m³'),
('o3', 100.0, 100.0, 'µg/m³');
