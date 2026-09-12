# Invoke Sql Insert

Runs an INSERT statement and reports how many rows were inserted. Python port of
[Invoke-SqlInsert.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Invoke-SqlInsert/Invoke-SqlInsert.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python invoke_sql_insert.py
python invoke_sql_insert.py --config-path SqlInsertConfig.json --query-path insert_query.sql
```

## Config (`SqlInsertConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |

The query lives in `insert_query.sql`, edited independently of the script — fill in
the `-- TODO` placeholder before running.

## Logging
Logs are written to `Logs/invoke_sql_insert_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
