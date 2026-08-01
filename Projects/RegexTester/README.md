# Regex Tester

Tests a regex pattern against sample text and shows every match, its position, and
any numbered/named capture groups.

## Prerequisites
None beyond the standard library.

## Run it
```
python regex_tester.py --pattern "\d+" --text "I have 2 cats and 15 dogs"
python regex_tester.py --pattern "(?P<user>\w+)@(?P<domain>\w+\.\w+)" --text "contact: ruchik@example.com"
python regex_tester.py --pattern "^error" --text-file app.log --flags im
```
Use `--text-file` instead of `--text` to test against a file's contents.

## Flags
`--flags` accepts any combination of: `i` (ignorecase), `m` (multiline), `s` (dotall),
`x` (verbose) — e.g. `--flags im`.

## Output
Per match: the matched text with its start/end position, every numbered capture group,
and every named capture group (`(?P<name>...)`).

## Errors
- Invalid regex syntax → clear error with Python's own regex error message, exit code 1
- Unknown flag letter → clear error, exit code 1
- Neither `--text` nor `--text-file` given → clear error, exit code 1

## Tested
Verified: a simple `\d+` match (2 matches, correct positions), named groups extracting
user/domain from two email addresses (both numbered and named group access), a
multiline+ignorecase (`im`) test correctly matching both `ERROR:` and `error:` lines
via `^error.*`, plus an invalid-pattern error and an invalid-flag error.

## Logging
Logs are written to `Logs/regex_tester_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (plain match, named groups, combined flags, both
  error cases)
