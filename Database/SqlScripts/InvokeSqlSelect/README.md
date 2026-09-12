# Invoke Sql Select

Runs a SELECT statement and prints the results as a simple auto-sized table. Python
port of [Invoke-SqlSelect.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Invoke-SqlSelect/Invoke-SqlSelect.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python invoke_sql_select.py
python invoke_sql_select.py --config-path SqlSelectConfig.json --query-path select_query.sql
```

## Config (`SqlSelectConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |

The query lives in `select_query.sql`, edited independently of the script — fill in
the `-- TODO` placeholder before running.

## Logging
Logs are written to `Logs/invoke_sql_select_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
