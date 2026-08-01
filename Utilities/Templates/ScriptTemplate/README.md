# Script Template

The starting point for every other script in this workspace. Mirrors the
conventions of the existing PowerShell [ScriptTemplate.ps1](../../../../../../../Ruchik/PowerShell/Utilities/Templates/ScriptTemplate/ScriptTemplate.ps1) -
SYNOPSIS/DESCRIPTION/EXAMPLE/NOTES docstring, daily-rotating log file with
retention and a per-run CorrelationID, module dependency checking, and a
try/except wrapper that logs failures and exits non-zero.

This file isn't meant to be run as-is for real work - it's a copy-paste
starting point.

## How to use it
1. Copy `ScriptTemplate.py` into a new script's folder and rename it.
2. Update the docstring (SYNOPSIS/DESCRIPTION/EXAMPLE/NOTES) for what the new
   script actually does.
3. Update `REQUIRED_MODULES` if the new script depends on third-party packages.
4. Update `parse_args()` for the new script's actual CLI arguments.
5. Replace the body of `main_process()` with the real logic.
6. Update `LOG_FILE_NAME`'s prefix and the logger name in `get_logger()` to
   match the new script's name.

## Run it (as a demo of the template itself)
```
python ScriptTemplate.py --site-url https://abc/sites/test
```
As shipped, `main_process()` looks for a `scriptname.json` config file next to
the script and exits with an error if it's missing - this is intentional,
demonstrating the "load config, validate, then act" shape most of this
workspace's scripts follow. Copy the template and replace this logic rather
than running the template unmodified.

## Logging
Logs are written to `Logs/scriptname_<date>.log`, with a per-run CorrelationID
and 7-day retention - every script built from this template inherits the same
pattern, e.g. [get_weather.py](../../../Projects/Weather/README.md).

## Status
- [x] Verified working as a template: compiles cleanly, and correctly exits
  with an error (not a crash) when the expected `scriptname.json` config file
  is absent, which is its documented behavior
