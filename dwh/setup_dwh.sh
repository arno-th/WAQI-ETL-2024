# Run this with `./setup_dwh.sh` from a shell terminal in `dwh` folder
cat ./createTables.sql | docker exec -i clickhouse clickhouse-client