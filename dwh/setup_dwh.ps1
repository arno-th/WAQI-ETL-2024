# Run this with `./setup_dwh.ps1` from a shell terminal in `dwh` folder
Get-Content .\createTables.sql | docker exec -i clickhouse clickhouse-client