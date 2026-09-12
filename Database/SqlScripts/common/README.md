# common

Shared helpers reused by every script under `Database/SqlScripts/`. Not meant to be
run directly. Python port of [SqlScripts.Common.psm1](../../../../../../Ruchik/powershell-scripts/Database/SqlScripts/Common/SqlScripts.Common.psm1).

## Prerequisites
```
pip install pyodbc
```
`pyodbc` also needs a SQL Server ODBC driver installed on the machine (e.g. **ODBC
Driver 17 for SQL Server** - the default `sql_common.py` assumes). Download from
Microsoft if `pip install pyodbc` succeeds but connecting fails with a driver-not-found
error.

## Files
- **`SqlServerConfig.json`** — the one place `Server`/`UserId`/`Password`/
  `TrustServerCertificate` live. Every script's own config file used to repeat the
  full connection string (as the original PowerShell scripts did); now each script's
  config only specifies what's actually different for that script — usually just
  `"Database"` — and `sql_common.build_connection_string()` fills in the rest from
  here. Change the password once here instead of in eleven places. Like every other
  `Sql*Config.json` in this folder, it holds a real plaintext SQL login and is
  tracked as-is (not `.gitignore`d).
- **`SqlServerConfig.example.json`** — placeholder copy of the above with dummy
  values, documenting the expected fields for anyone setting up against a different
  server/login.
- **`db_logging.py`** — `build_logger(script_folder, script_name)` returns `(logger, correlation_id)`:
  sets up a logger writing to `<script_folder>/Logs/<script_name>_<date>.log` with
  7-day retention, and a per-run CorrelationID.
- **`sql_common.py`** — SQL Server helpers built on `pyodbc`:

  | Function | Purpose |
  |---|---|
  | `get_sql_script_config(config_path)` | Reads a JSON config file and returns it as a dict. |
  | `build_connection_string(database)` | Builds an ADO.NET-style connection string for `database`, using the shared `Server`/`UserId`/`Password`/`TrustServerCertificate` from `SqlServerConfig.json`. `database` can also be `"{0}"` as a template placeholder (see [ExportTenantSubscriptionsToCsv](../ExportTenantSubscriptionsToCsv/README.md)). |
  | `invoke_sql_non_query(connection_string, query, command_timeout=30)` | Runs a non-query (INSERT/UPDATE/DELETE/DDL) and returns rows affected. |
  | `invoke_sql_query(connection_string, query, command_timeout=30)` | Runs a query and returns `(columns, rows)` — `rows` is a list of `{column: value}` dicts. |
  | `bulk_insert(connection_string, table_name, rows)` | Inserts a list of same-shaped dicts via a parameterized `fast_executemany` INSERT — the Python equivalent of `SqlBulkCopy`. |
  | `print_table(columns, rows)` | Prints rows as a simple auto-sized table, similar in spirit to `Format-Table -AutoSize`. |

  `build_connection_string()`'s output still uses the original ADO.NET-style format
  (`Server=...;Database=...;User Id=...;Password=...;TrustServerCertificate=True;`);
  the query/non-query/bulk-insert functions translate it to the ODBC keys `pyodbc`
  expects (`Uid`/`Pwd`, `Yes`/`No`, a `Driver=...` prefix) internally.

  Every connection also registers a decoder for SQL Server's `datetimeoffset` type
  (ODBC SQL type `-155`), which `pyodbc` can't read out of the box — without it,
  any query touching a `datetimeoffset` column (e.g. `Common.Tenant.Subscription`'s
  `ExpiresOn`) fails with `"ODBC SQL type -155 is not yet supported"`.

## How scripts import this
Since each script lives in its own sibling folder (not a proper installed package),
every script adds `common/` to `sys.path` at the top before importing:

```python
SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER.parent / "common"))

import db_logging
import sql_common
```

Note: IDEs (Pylance/VS Code) may show "Import could not be resolved" for `db_logging`
or `sql_common` since they can't see the runtime `sys.path` change - this is a false
warning, not a real error.

## Used by
- [InvokeSqlSelect](../InvokeSqlSelect/README.md)
- [InvokeSqlInsert](../InvokeSqlInsert/README.md)
- [InvokeSqlUpdate](../InvokeSqlUpdate/README.md)
- [InvokeSqlDelete](../InvokeSqlDelete/README.md)
- [ExportSqlQueryToCsv](../ExportSqlQueryToCsv/README.md)
- [ImportCsvToSql](../ImportCsvToSql/README.md)
- [InvokeSqlScriptFile](../InvokeSqlScriptFile/README.md)
- [BackupSqlDatabase](../BackupSqlDatabase/README.md)
- [UpdateEffortEntryType](../UpdateEffortEntryType/README.md)
- [GetTenantDatabaseMapping](../GetTenantDatabaseMapping/README.md)
- [ExportTenantSubscriptionsToCsv](../ExportTenantSubscriptionsToCsv/README.md)
