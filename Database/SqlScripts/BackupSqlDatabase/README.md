# Backup Sql Database

Runs `BACKUP DATABASE` against the database named in the config's connection string,
writing a timestamped `.bak` file. Python port of
[Backup-SqlDatabase.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Backup-SqlDatabase/Backup-SqlDatabase.ps1).

> **Note:** `BackupDirectory` is a path on the **SQL Server host itself**, not the
> machine running this script — SQL Server writes the backup file server-side.

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python backup_sql_database.py
python backup_sql_database.py --config-path SqlBackupConfig.json
```

## Config (`SqlBackupConfig.json`)

| Field | Description |
|---|---|
| `Database` | Database to back up — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. |
| `BackupDirectory` | Server-side folder to write the `.bak` file into. |

Output file is named `<DatabaseName>_<yyyyMMdd_HHmmss>.bak`. Runs with
`command_timeout=0` (no timeout), since backups can run long.

## Logging
Logs are written to `Logs/backup_sql_database_<date>.log`, with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
