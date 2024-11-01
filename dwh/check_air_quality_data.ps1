# Run this with `./check_air_quality_data.ps1` from a shell terminal in `dwh` folder
Get-Content .\air_quality_data.sql | docker exec -i clickhouse clickhouse-client