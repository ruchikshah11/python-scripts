# Duplicate File Finder

Finds exact duplicate files under a folder (recursively) by content hash, and reports
them grouped together with wasted space. Can also delete duplicates, keeping one copy
per group — **defaults to a dry run**; nothing is deleted until you pass `--delete`.

## Prerequisites
None beyond the standard library.

## Run it
```
# Report only (default) - nothing is deleted
python find_duplicates.py --path "C:/Users/me/Downloads"

# Delete duplicates, keeping the alphabetically-first copy of each group
python find_duplicates.py --path "C:/Users/me/Downloads" --delete

# Keep the oldest/newest copy instead, and skip the confirmation prompt
python find_duplicates.py --path "C:/Users/me/Downloads" --delete --keep oldest --yes
```

## How it works
1. Scans every file under `--path` recursively, grouping by file size first (cheap).
2. Only hashes (SHA-256) files that share a size with at least one other file —
   avoids hashing every file when most sizes are unique.
3. Groups by hash; any group with 2+ files is a duplicate set.

## Safety
- **Dry run by default** — must pass `--delete` to remove anything
- **Confirmation prompt** before deleting, unless `--yes` is also passed
- `--keep {first,oldest,newest}` controls which copy survives per group (default `first`,
  alphabetically)

## Tested
Verified against a scratch folder with 3 identical files (one in a subfolder, to
confirm recursion) + a separate duplicate pair + one unique file: dry run correctly
identified both groups without touching anything; `--delete --yes` correctly kept one
file per group (verified the right survivor per `--keep` rule) and left the unique
file alone.

## Logging
Logs are written to `Logs/find_duplicates_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (dry run, delete with each --keep option's logic,
  confirmation skip via --yes) — all tested against a scratch folder, not real files
