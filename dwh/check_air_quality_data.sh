# Run this with `./check_air_quality_data.sh` from a shell terminal in `dwh` folder
cat ./air_quality_data.sql | docker exec -i clickhouse clickhouse-client