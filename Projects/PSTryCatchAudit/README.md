# PS Try/Catch Audit

A one-off diagnostic script written while cleaning up an AI-assisted change to
`Invoke-bsoneDeployment.ps1` that had wrapped nearly every function in a
swallow-and-log `try/catch`, letting critical failures (execution policy,
missing config files, etc.) pass silently instead of stopping the script.

`ps_trycatch_audit.py` compares the working-tree PowerShell file against its
`git HEAD` version and lists every function whose *entire body* became a new
top-level `try/catch` — candidates for manual removal so exceptions propagate
normally again.

## Usage

```
git show HEAD:path/to/File.ps1 > Original.ps1
python ps_trycatch_audit.py path/to/File.ps1 Original.ps1
```

## Limitations

Uses a hand-rolled brace matcher (tracks quotes and `#` / `<# #>` comments),
not a real PowerShell parser. Here-strings aren't handled, and functions using
`Param()`/`Process {}` blocks (advanced functions) won't be detected if the
`try` is nested inside `Process {}` rather than right after the function's own
opening brace. Treat the output as a starting point and cross-check anything
it misses (or reports as a parse failure) against the actual `git diff`.
