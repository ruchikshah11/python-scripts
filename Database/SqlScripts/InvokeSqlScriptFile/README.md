# Invoke Sql Script File

Runs a multi-batch `.sql` file (e.g. a migration) the same way SSMS would — splits
the file on lines containing only `GO` and executes each batch in turn. Python port
of [Invoke-SqlScriptFile.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Invoke-SqlScriptFile/Invoke-SqlScriptFile.ps1).

Use this instead of the single-statement `invoke_sql_*.py` scripts when a script
needs multiple batches (e.g. DDL followed by DML, or statements that must run
separately).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python invoke_sql_script_file.py
python invoke_sql_script_file.py --config-path SqlScriptFileConfig.json --script-path migration_script.sql
```

## Config (`SqlScriptFileConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |
| `CommandTimeout` | Per-batch timeout in seconds (default 30). |

Prints/logs rows affected per batch and a total at the end.

## Logging
Logs are written to `Logs/invoke_sql_script_file_<date>.log`, with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
