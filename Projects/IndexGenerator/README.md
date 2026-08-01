# Index Generator

Scans every `.py` script under the Python project root and generates
[`INDEX.md`](../../INDEX.md) at the root — a single catalog file listing every
project/script with its one-line SYNOPSIS description, extracted directly from each
script's own docstring. Similar in spirit to a PowerShell comment-based help catalog,
adapted for this Python workspace.

## Prerequisites
None beyond the standard library.

## Run it
```
python generate_index.py
python generate_index.py --root "C:/Users/ruchik.shah/Downloads/Python"
```
Re-run any time you add or change scripts — `INDEX.md` is generated output, not meant
to be hand-edited.

## How it works
1. Recursively finds every `*.py` file under `--root`, skipping `__pycache__`, `Logs`,
   virtual environment folders, and itself.
2. For each file, parses it with Python's `ast` module (never executes it) and pulls
   the module's docstring via `ast.get_docstring()`.
3. Regex-extracts the text between a `SYNOPSIS` header and the next all-caps section
   header (`DESCRIPTION`, `EXAMPLE`, `NOTES`) — falling back to the docstring's first
   paragraph if there's no `SYNOPSIS` section, or `(no SYNOPSIS found)` if there's no
   docstring at all.
4. Collapses the (often multi-line, indented) SYNOPSIS text into one clean line.
5. Groups entries by top-level folder and writes `INDEX.md`.

Using `ast` instead of just running each script means this is completely safe to run
against scripts that would otherwise open a browser for SharePoint auth, hit real
APIs, or prompt for input — none of that code ever executes, only the docstring is read.

## Tested
Ran live against this entire workspace: found 85 Python files across 25 folders,
correctly extracted and collapsed multi-line SYNOPSIS blocks for 84 of them, and
correctly flagged the one file with no docstring at all (`HelloWorld/hello_world.py`)
rather than crashing or guessing.

## Logging
Logs are written to `Logs/generate_index_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end against the real workspace (85 files, 25 folders,
  1 correctly-flagged missing SYNOPSIS)
