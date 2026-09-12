# Export Tenant Subscriptions To Csv

Exports `[dbo].[Common.Tenant.Subscription]` from every tenant database into a single
CSV. Python port of
[Export-TenantSubscriptionsToCsv.ps1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Export-TenantSubscriptionsToCsv/Export-TenantSubscriptionsToCsv.ps1).

`tenant_database_mapping.sql` resolves each tenant's database the same way as
[GetTenantDatabaseMapping](../GetTenantDatabaseMapping/README.md) (`Tenant` ->
`Tenant.Credential` -> `Server.Instance.Database.Name`). The script then queries
each **distinct** resolved database once (not once per tenant row — several
companies can be provisioned into one shared database) with `subscription_query.sql`,
and for every row returned looks up `CompanyName` from that row's own `TenantID` via
a `TenantID -> CompanyName` map built from the mapping query - that's what actually
identifies the owner when a database is shared.

> **Note:** this ports the PowerShell script's actual behavior — one query per
> distinct tenant database, looped in Python. (An earlier revision of the PS1's own
> README described a single cross-database `UNION ALL` / `sp_executesql` design, but
> the `.ps1` that ships alongside it does the per-database loop described here; this
> port follows the code, not the stale README text.)

Read-only throughout (no `CREATE`/`INSERT`/`UPDATE`/`DELETE`); both `.sql` files use
`WITH (NOLOCK)` so this reporting run can't block, or get blocked by, live
production traffic.

Output columns: `CompanyName`, `SourceDatabase`, `TenantID`,
`SubscriptionIdentifier`, `ClientState`, `SiteUrl`, `NotificationUrl`, `Resource`,
`ExpiresOn`, `ChangeToken`, `IsDeleted`, `ChangeType`, `ContactID`,
`DBModifiedOn`, `UpdateSource`.

Tenants with no configured database, or whose database can't be reached or doesn't
have the table, are logged with a warning and skipped rather than aborting the whole
export.

## Prerequisites
```
pip install pyodbc
```
Also needs a SQL Server ODBC driver installed (see [common](../common/README.md)).

## Run it
```
python export_tenant_subscriptions_to_csv.py
python export_tenant_subscriptions_to_csv.py --config-path SqlTenantSubscriptionExportConfig.json --mapping-query-path tenant_database_mapping.sql --subscription-query-path subscription_query.sql
```

## Config (`SqlTenantSubscriptionExportConfig.json`)

| Field | Description |
|---|---|
| `Database` | `bsone_core` — combined with the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` in [common/SqlServerConfig.json](../common/SqlServerConfig.json) for the tenant/database mapping lookup. |
| `OutputPath` | CSV output path. Relative paths are resolved next to this script. |

The per-tenant connection string (one per distinct resolved database) is built the
same way, via `sql_common.build_connection_string("{0}")` — a template with a
literal `{0}` placeholder that gets `.format()`-substituted with each database name
in turn.

`Common.Tenant.Subscription`'s `ExpiresOn`/`DBModifiedOn` columns are SQL Server
`datetimeoffset` - `sql_common`'s shared connection helper registers a decoder for
that type (`pyodbc` can't read it natively), so this export doesn't fail with
`"ODBC SQL type -155 is not yet supported"`.

## Logging
Logs are written to `Logs/export_tenant_subscriptions_to_csv_<date>.log`, with a
per-run CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).
Per-database progress (`(N of M) Exporting <database>`) and skip warnings are also
logged, in place of the PowerShell version's `Write-Progress`/`Write-Warning`.

## Status
- [ ] Verified working end-to-end
