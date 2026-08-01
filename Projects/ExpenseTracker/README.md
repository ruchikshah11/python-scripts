# Expense Tracker

A CLI expense tracker backed by SQLite — add, list, summarize (by category, with an
optional month filter), and delete expenses. The database file (`expenses.db`) is
created automatically next to the script on first use.

## Prerequisites
None beyond the standard library.

## Run it
```
python expense_tracker.py add 45.50 --category Groceries --description "Weekly shop"
python expense_tracker.py add 12 --category Transport --date 2026-07-06

python expense_tracker.py list                      # everything
python expense_tracker.py list --month 2026-07       # filter by month
python expense_tracker.py list --category Groceries  # filter by category

python expense_tracker.py summary                    # totals per category, all time
python expense_tracker.py summary --month 2026-07
python expense_tracker.py summary --export-csv july_summary.csv

python expense_tracker.py delete 3
```
`--date` defaults to today if omitted.

## Ties into ReportBuilder
`summary --export-csv` writes a CSV shaped like:
```
Category,Total,Count
Groceries,135.49,2
...
TOTAL,177.49,
```
Feed that straight into [ReportBuilder](../ReportBuilder/README.md)'s
`build_report.py --input july_summary.csv --output july_summary.xlsx` for a formatted
Excel/PDF report — the two tools are deliberately kept separate/decoupled but compose
via CSV.

## Errors
- `delete` on a non-existent expense ID → clear error, exit code 1

## Tested
Verified end-to-end: added 4 expenses across 2 months/3 categories; `list` with no
filter, `--month`, and `--category` all returned the correct subsets; `summary`
totals matched hand-calculated sums (Groceries 135.49, grand total 177.49 all-time /
147.49 for July); `--export-csv` produced a correct CSV; `delete` removed the right
row; deleting a non-existent ID errored cleanly.

## Logging
Logs are written to `Logs/expense_tracker_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (add, all list filters, summary math, CSV export,
  delete, and the not-found error case)
