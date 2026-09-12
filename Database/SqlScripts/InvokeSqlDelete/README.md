# Invoke Sql Delete

Runs a DELETE statement and reports how many rows were deleted. Python port of
[Invoke-SqlDelete.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Invoke-SqlDelete/Invoke-SqlDelete.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python invoke_sql_delete.py
python invoke_sql_delete.py --config-path SqlDeleteConfig.json --query-path delete_query.sql
```

## Config (`SqlDeleteConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |

The query lives in `delete_query.sql`, edited independently of the script — fill in
the `-- TODO` placeholder before running. Double-check the `WHERE` clause before
executing; there is no dry-run mode.

## Logging
Logs are written to `Logs/invoke_sql_delete_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
