# Password Tool

Generates cryptographically secure random passwords (via Python's `secrets` module,
not `random`), or checks the strength of an existing password with specific feedback.

## Prerequisites
None beyond the standard library.

## Run it
```
python password_tool.py generate
python password_tool.py generate --length 20 --count 3
python password_tool.py generate --no-symbols

python password_tool.py check --password "Tr0ub4dor&3"
python password_tool.py check    # omit --password to get a hidden interactive prompt instead
```

## Generate
- `--length` (default 16), `--count` (default 1)
- `--no-uppercase` / `--no-lowercase` / `--no-digits` / `--no-symbols` to exclude a
  character category
- Guarantees at least one character from each enabled category, then fills the rest
  and shuffles securely (Fisher-Yates using `secrets.randbelow`)
- `--length` shorter than the number of enabled categories → clear error, exit code 1

## Check
Scores 0–100 with a label (Very Weak / Weak / Fair / Strong / Very Strong), based on:
length, character variety (lower/upper/digit/symbol), whether it's in a small built-in
list of extremely common passwords, repeated-character runs (`aaa`), and sequential
runs (`abc`, `123`, or their reverse). Gives specific feedback per issue found.

## Security notes
- **Generated passwords are printed directly to the console — never written to the
  log file.** The operational logger only records that a generation happened (count,
  length), not the password itself, since that's a secret that must not be persisted
  to disk.
- **Checked passwords are never logged either** — only the resulting score/feedback.
- `check --password` on the command line still ends up in shell history. Prefer
  omitting `--password` to get a hidden `getpass` prompt instead.
- **`getpass` prompt caveat**: on Windows, `getpass.getpass()` reads directly from the
  console and does not work with piped/redirected input — it needs a real interactive
  terminal. I could not verify this prompt path myself in my sandboxed test
  environment (it hung waiting for console input when I piped a value in and I had to
  cancel it) — please test it yourself in a real PowerShell/terminal session. The
  `--password` argument path is fully tested and works.

## Logging
Logs are written to `Logs/password_tool_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).
Contains no passwords, per the security notes above.

## Status
- [x] Verified working: generate (default, custom length/count, no-symbols), check
  (weak/common password, decent password with a sequential-run catch, repeated+sequential
  combo), and the too-short --length error
- [ ] Interactive `getpass` prompt - untested here (see caveat above), please verify
  in your own terminal
