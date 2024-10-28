SELECT 'Dropping and recreating [air_quality]';
DROP TABLE IF EXISTS air_quality;

CREATE TABLE air_quality (
    station_id UInt32,
    station_name String,
    data_timestamp DateTime,
    aqi UInt8,
    dominant_pollutant String
) ENGINE = MergeTree()
ORDER BY (station_id, data_timestamp);
SELECT 'Created [air_quality]';

SHOW TABLES;

DESCRIBE air_quality;