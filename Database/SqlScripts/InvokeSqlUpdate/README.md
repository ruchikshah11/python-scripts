# Invoke Sql Update

Runs an UPDATE statement and reports how many rows were updated. Python port of
[Invoke-SqlUpdate.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Invoke-SqlUpdate/Invoke-SqlUpdate.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python invoke_sql_update.py
python invoke_sql_update.py --config-path SqlUpdateConfig.json --query-path update_query.sql
```

## Config (`SqlUpdateConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |

The query lives in `update_query.sql`, edited independently of the script — fill in
the `-- TODO` placeholder before running.

## Logging
Logs are written to `Logs/invoke_sql_update_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
