# Personal Dashboard

A single-window "at a glance" dashboard combining current weather, pending to-do
tasks, and this month's expense summary — all refreshing automatically on open.
Reuses the tested functions/data files from [Weather](../../Projects/Weather/README.md),
[TodoManager](../../Projects/TodoManager/README.md), and [ExpenseTracker](../../Projects/ExpenseTracker/README.md)
directly, rather than a tabbed toolbox you click into — open it, read it, close it.

## Prerequisites
```
pip install requests
```

## Run it
```
python personal_dashboard.py
```
All three panels load automatically. Each has its own **Refresh** button; Weather also
has a location field (defaults to Zurich) if you want a different city.

## Panels
| Panel | Source | Notes |
|---|---|---|
| Weather | `Projects/Weather/get_weather.py` | Current conditions only (not the 5-day forecast); runs on a background thread so the window appears immediately |
| To-Do | `Projects/TodoManager/todo.db` | Pending tasks only, same database as the CLI tool and the Toolbox GUI |
| Expenses | `Projects/ExpenseTracker/expenses.db` | **Current calendar month only** — category totals + grand total |

If either database file doesn't exist yet (no tasks/expenses added), each panel shows
a friendly placeholder instead of erroring.

## Tested
Unlike SharePoint Explorer, this app needs no credentials I don't have — I launched it
directly: it started, made a real call to the Weather API for Zurich, and stayed
running without crashing (confirmed via a timed run that only stopped because I killed
it, not because it errored). To-Do/Expense panels were exercised against real
`todo.db`/`expenses.db` files from earlier testing in this workspace.

**Not verified**: the actual visual layout/spacing — I have no screenshot capability,
so please glance at the window yourself to confirm it looks right.

## Logging
None — this is meant to be a quiet, glanceable widget. Errors (e.g. weather API
failures) show inline in the relevant panel's text instead of a separate log panel.

## Status
- [x] Launched successfully, real Weather API call confirmed working, To-Do/Expense
  panels read real data correctly
- [ ] Visual layout — please confirm it looks right, I can't see it myself
