# Log Analyzer

Scans every `Logs/` folder under a project root (recursively) and summarizes runs,
successes, failures, durations, and ERROR-level line counts per script — across every
script in this workspace that uses the shared daily-log-file/CorrelationID logging
pattern (`ScriptTemplate.py`, the SharePoint scripts, `get_weather.py`, etc.).

## Prerequisites
None beyond the standard library.

## Run it
```
python analyze_logs.py
python analyze_logs.py --root "C:/Users/ruchik.shah/Downloads/Python"
python analyze_logs.py --output summary.json
```
`--root` defaults to the parent of this script's folder (i.e. `Downloads/Python`).

## Output
- Overall totals: scripts analyzed, total runs, total failures, total ERROR lines
- Per script: runs / successes / failures / error lines, average/min/max duration in
  seconds, last run timestamp, and the most recent failure's details (if any)
- `--output <path>`: also writes the same data as JSON

## How parsing works
Reads each `*.log` file inside any `Logs/` folder, matching lines against the shared
format `"<timestamp> <LEVEL>\t<message>"`. Recognizes three message patterns:
`Script started at ...`, `Script finished at ..., time taken: <n>s ...`, and
`Script failed at ..., time taken: <n>s ... Details: ...` — plus counts every
`ERROR`-level line regardless of pattern. The script name is taken from the log file
name (`<script_name>_<yyyyMMdd>.log`).

## ⚠️ Finding: Logs are disappearing on their own
While building and testing this, I found that `Logs/` folders in this workspace get
deleted or wiped shortly after being created — not by any script here, and not by the
7-day retention logic (`delete_old_logs()` only removes files older than 7 days, and
this happened to same-day files within seconds/minutes). Confirmed two ways:
1. `CurrencyConverter/Logs/` existed immediately after a run, then was gone entirely
   on a later check.
2. `analyze_logs`'s own log file, opened in Python's default append mode, only ever
   contained the most recent run's lines — a prior run's entries had vanished, as if
   the file were recreated fresh rather than appended to.

This means actual log retention across every script in this workspace may be much
shorter than the 7 days each script intends. Likely causes on a managed/work machine:
antivirus or endpoint security (Defender, CrowdStrike, etc.) treating new `.log` files
as suspicious, a scheduled cleanup task, or Controlled Folder Access. Worth checking
with whoever manages this machine's security policy if log persistence matters to you.

## Logging
Logs are written to `Logs/analyze_logs_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).
Note: per the finding above, this script's own logs are not immune to whatever is
clearing them.

## Status
- [x] Verified working end-to-end against real logs in this workspace (correctly
  parsed `get_list_items`'s successful run with duration, and its own self-referential
  run)
- [ ] Root cause of disappearing Logs/ folders - unresolved, needs investigation on
  your end (see finding above)
