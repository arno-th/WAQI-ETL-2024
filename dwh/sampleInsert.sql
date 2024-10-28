--Use this to test dwh docker container write capability
INSERT INTO air_quality (station_id, station_name, data_timestamp, aqi, dominant_pollutant)
VALUES
(1, 'Station 1', '2024-01-01T12:00:00', 12, 'Hydrogen')