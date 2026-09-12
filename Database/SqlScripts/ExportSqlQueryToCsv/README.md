# Export Sql Query To Csv

Runs a SQL query and exports the results to CSV. Python port of
[Export-SqlQueryToCsv.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Export-SqlQueryToCsv/Export-SqlQueryToCsv.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python export_sql_query_to_csv.py
python export_sql_query_to_csv.py --config-path SqlExportConfig.json --query-path effort_query.sql
```

## Config (`SqlExportConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |
| `OutputPath` | CSV output path. Relative paths are resolved next to this script. |

The query lives in `effort_query.sql` (default), edited independently of the script.
The bundled query pulls `Project.Activity.Effort` rows for a given `AssignedToID` from
the last 30 days with `EntryTypeID = 2`.

## Logging
Logs are written to `Logs/export_sql_query_to_csv_<date>.log`, with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end against the real tenant database (connected,
  ran `effort_query.sql`, wrote `EffortExport.csv` - 0 rows matched at test time)
