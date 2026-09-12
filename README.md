# Python

A personal Python workspace: learning material, ~20 standalone CLI utilities, a
pattern-printing library, a small SharePoint library (there's no PnP for Python),
and a handful of Tkinter desktop apps built on top of the CLI tools. Conventions
(logging with rotation/retention/CorrelationID, SYNOPSIS/DESCRIPTION/EXAMPLE/NOTES
docstrings) are carried over from an existing PowerShell scripting background.

See **[INDEX.md](INDEX.md)** for a full, auto-generated catalog of every script
with its one-line description (103 scripts across 8 categories as of writing).

## Table of Contents
- [Structure](#structure)
- [Prerequisites](#prerequisites)
- [Conventions](#conventions)

## Structure

| Folder | What's in it |
|---|---|
| [Learning/](Learning) | 9 step-by-step lessons (variables → REST APIs), PowerShell-to-Python comparisons throughout |
| [Patterns/](Patterns) | 26 classic pattern-printing programs (Pyramid, Diamond, Pascal's Triangle, etc.), each with its own README + sample output |
| [Projects/](Projects) | ~17 standalone CLI utilities (Weather, Currency Converter, Password Tool, To-Do Manager, Expense Tracker, QR Code Generator, and more) |
| [DesktopApps/](DesktopApps) | 5 Tkinter GUIs that reuse the Projects/ tools' (and the `sharepoint` library's) actual functions rather than reimplementing logic (Utility Toolbox, Personal Dashboard, SharePoint Explorer, Pattern Visualizer, SP Dummy Data Generator) |
| [SharePoint/](SharePoint) | A personal `sharepoint` library (Office365-REST-Python-Client + msal) plus one CLI script per operation, mirroring PnP PowerShell's coverage |
| [Database/SqlScripts/](Database/SqlScripts) | A `sql_common` library (pyodbc) plus 11 CLI scripts (SELECT/INSERT/UPDATE/DELETE, CSV export/import, multi-batch script runner, DB backup, tenant/database mapping and subscription export) - ported from the equivalent PowerShell `SqlScripts` family |
| [Utilities/Templates/](Utilities/Templates) | `ScriptTemplate.py` - the starting point every other script here is built from |
| [HelloWorld/](HelloWorld) | The very first script - confirms Python runs before anything else was built |

## Prerequisites

- **Python 3.8+** (some scripts use the walrus operator). Developed and tested on
  Windows with PowerShell; paths in code use `pathlib`, so it should run unmodified
  on macOS/Linux too.
- Third-party packages used across the workspace:
  ```
  pip install requests office365-rest-python-client msal pillow qrcode reportlab openpyxl Faker pyodbc
  ```
  Each folder's own README lists exactly what that script needs - not every script
  needs every package above. Every script also self-checks its own required modules
  at startup and exits with a clear message (not a raw `ImportError` traceback) if
  something's missing.
- Nothing here requires an API key - Weather (Open-Meteo), Currency (Frankfurter),
  GitHub Stats, and quote/joke APIs were all deliberately chosen because they're free
  and keyless.
- **SharePoint/** scripts are the one exception: they need an existing Azure AD app
  registration (a client ID and tenant ID, passed as CLI args/config - see
  [SharePoint/sharepoint](SharePoint/sharepoint/README.md)) with permissions to the
  target site, since auth is interactive MSAL sign-in (a browser window opens) rather
  than key-based.
- **Database/SqlScripts/** scripts need a SQL Server ODBC driver installed
  (e.g. **ODBC Driver 17 for SQL Server**) in addition to `pip install pyodbc` - see
  [Database/SqlScripts/common](Database/SqlScripts/common/README.md).
- No `requirements.txt` yet - the `pip install` line above covers every third-party
  package this workspace currently uses.

## Conventions

- Every script follows [ScriptTemplate.py](Utilities/Templates/ScriptTemplate/README.md)'s
  shape: a SYNOPSIS/DESCRIPTION/EXAMPLE/NOTES docstring, daily-rotating logs under
  `Logs/` with a per-run CorrelationID and 7-day retention, module dependency
  checks, and a try/except wrapper that logs failures and exits non-zero.
- Every folder has its own README with what it does, how to run it, and what's
  actually been tested vs. what still needs a human to verify (mainly interactive
  SharePoint auth and GUI visual layout, which can't be exercised headlessly).
- `INDEX.md` is generated, not hand-edited - re-run
  [generate_index.py](Projects/IndexGenerator/README.md) after adding or changing
  scripts.
