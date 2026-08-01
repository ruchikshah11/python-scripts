# To-Do Manager

A CLI to-do list manager backed by SQLite — add, list, complete, and delete tasks.
The database file (`todo.db`) is created automatically next to the script on first use.

## Prerequisites
None beyond the standard library (`sqlite3` is built in).

## Run it
```
python todo_manager.py add "Buy milk"
python todo_manager.py add "Finish report" --due 2026-08-01

python todo_manager.py list                # pending tasks only (default)
python todo_manager.py list --all          # everything, pending + completed
python todo_manager.py list --completed    # completed tasks only

python todo_manager.py complete 2
python todo_manager.py delete 3
```

## Output format
```
[ ] #1 Buy milk
[x] #2 Finish report (due 2026-08-01) (completed 2026-07-30T11:28:58)
```
`[ ]` = pending, `[x]` = completed, due date and completion timestamp shown when set.

## Errors
- `complete`/`delete` on a non-existent (or already-completed, for `complete`) task
  ID → clear error message, exit code 1

## Data
Tasks are stored in `todo.db` (SQLite) next to the script — back it up like any other
file if you want to keep your task history. Schema: `id, text, due_date, completed,
created_at, completed_at`.

## Logging
Logs are written to `Logs/todo_manager_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (add, list in all 3 modes, complete, delete, and
  both not-found error cases)
