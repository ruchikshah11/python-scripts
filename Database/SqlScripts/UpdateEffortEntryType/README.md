# Update Effort Entry Type

One-off fix: sets `EntryTypeID = 1` on specific `Project.Activity.Effort` rows
(`AssignedToID` 47, `ID` 325566 and 325531), correcting rows originally surfaced by
[ExportSqlQueryToCsv](../ExportSqlQueryToCsv/README.md)'s `effort_query.sql` lookup
(`AssignedToID = 47`, `EntryTypeID = 2`, last 30 days). Python port of
[Update-EffortEntryType.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Update-EffortEntryType/Update-EffortEntryType.ps1).

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python update_effort_entry_type.py
python update_effort_entry_type.py --config-path SqlUpdateEffortEntryTypeConfig.json --query-path update_effort_entry_type.sql
```

## Config (`SqlUpdateEffortEntryTypeConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |

The UPDATE statement lives in `update_effort_entry_type.sql`. Scoped to specific rows
— not intended to be reused for other IDs without editing the `.sql` file.

## Logging
Logs are written to `Logs/update_effort_entry_type_<date>.log`, with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
