# Import Csv To Sql

Bulk-imports a CSV file into a table via a parameterized, `fast_executemany` INSERT —
the Python equivalent of `SqlBulkCopy`. The reverse of
[ExportSqlQueryToCsv](../ExportSqlQueryToCsv/README.md). Python port of
[Import-CsvToSql.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Import-CsvToSql/Import-CsvToSql.ps1).

The CSV's header row must match the destination table's column names exactly.

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python import_csv_to_sql.py
python import_csv_to_sql.py --config-path SqlImportConfig.json --csv-path import_data.csv
```

## Config (`SqlImportConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database name — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |
| `TableName` | Destination table (schema-qualified, e.g. `dbo.YourTable`). |
| `TruncateBeforeImport` | If `true`, truncates the table before loading. |

## Logging
Logs are written to `Logs/import_csv_to_sql_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
