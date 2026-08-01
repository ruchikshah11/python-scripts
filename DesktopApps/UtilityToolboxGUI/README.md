# Utility Toolbox GUI

A Tkinter desktop app wrapping several of this workspace's standalone CLI utilities
behind one tabbed window — **reusing their tested functions directly** rather than
reimplementing any logic.

## Prerequisites
```
pip install pillow
```
(Everything else needed — `requests` for Weather/Currency — is already installed from
building those tools.)

## Run it
```
python toolbox_gui.py
```

## Tabs
| Tab | Wraps | Notes |
|---|---|---|
| **Weather** | `Weather/get_weather.py` | Current + 5-day forecast, runs on a background thread so the UI doesn't freeze during the API call |
| **Currency** | `CurrencyConverter/convert_currency.py` | Same-currency case handled specially, same as the CLI version |
| **Units** | `UnitConverter/convert_units.py` | Category dropdown drives which units are offered |
| **QR Code** | `QRCodeGenerator/generate_qr.py` | Save-as dialog, then shows a live thumbnail preview |
| **Password** | `PasswordTool/password_tool.py` | Generate (with category checkboxes) and Check (with show/hide toggle) in one tab |
| **To-Do** | `TodoManager/todo_manager.py` | Reads/writes the *same* `TodoManager/todo.db` — data stays in sync with the CLI tool |
| **Expenses** | `ExpenseTracker/expense_tracker.py` | Reads/writes the *same* `ExpenseTracker/expenses.db`, plus a Show Summary button |

A status/log panel at the bottom shows what's happening — it's fed by the actual
`logger.info(...)` calls inside the imported Weather/Currency functions, not a
separate fake log.

## How the integration works
Each tab adds its tool's sibling folder to `sys.path` and imports the specific
functions it needs (e.g. `get_weather.geocode_location`, `password_tool.generate_password`).
No CLI script's code was duplicated or modified. The To-Do/Expense tabs are the one
exception — those tools' `list`/`summary` functions only print via their logger rather
than returning data, so the GUI runs its own minimal `SELECT` queries directly against
the same database files for display purposes (add/complete/delete still reuse the
real functions).

## Tested
Verified: compiles cleanly, all 7 sibling-tool imports resolve without error, and the
app launches without an immediate crash (confirmed no traceback in the process output
after startup). **I can't interact with or visually verify the GUI myself** — no
screenshot capability in this environment — so please click through each tab
yourself and confirm the widgets behave as expected.

## Logging
No separate log file — status messages appear in the in-app text panel only (backed
by the real loggers from the imported Weather/Currency modules).

## Status
- [x] Compiles, imports, and launches without crashing
- [ ] **Visual/interactive verification — please test each tab yourself**, I have no
  way to see or click the actual window
