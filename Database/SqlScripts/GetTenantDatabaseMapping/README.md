# Get Tenant Database Mapping

Lists every tenant alongside the database it's configured to use, by joining:

1. `[bsone_core].[dbo].[Tenant]` — `ID`, `CompanyName`
2. `[bsone_core].[dbo].[Tenant.Credential]` — links `TenantID` to `DatabaseID`
3. `[bsone_core].[dbo].[Server.Instance.Database]` — resolves `DatabaseID` to the
   actual database `Name`

Output columns: `TenantID`, `CompanyName`, `ConfiguredDatabaseName`. Python port of
[Get-TenantDatabaseMapping.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Get-TenantDatabaseMapping/Get-TenantDatabaseMapping.ps1).

Uses `LEFT JOIN`s throughout, so tenants without a credential/database record still
appear (with `NULL`/empty for `ConfiguredDatabaseName`) instead of being silently
dropped.

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python get_tenant_database_mapping.py
python get_tenant_database_mapping.py --config-path SqlTenantDatabaseMappingConfig.json --query-path tenant_database_mapping.sql
```

## Config (`SqlTenantDatabaseMappingConfig.json`)

| Field | Description |
|---|---|
| `Database` | `bsone_core` — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) to build the connection string. (The tables are fully qualified with `[bsone_core]` in the query too, but the login/server still need to be reachable.) |

The SELECT statement lives in `tenant_database_mapping.sql`.

## Logging
Logs are written to `Logs/get_tenant_database_mapping_<date>.log`, with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
