# Lesson 1: Variables, Types, and Basic I/O

## Topics
- Variables (no sigil, no type declaration — unlike PowerShell's `$name`)
- Types: `str`, `int`, `bool` and checking with `type(x).__name__`
- f-strings for formatting: `f"Hello {name}"` (vs PowerShell's `"Hello $name"`)
- Output with `print()` (vs `Write-Host`)
- Input with `input()` (vs `Read-Host`) — always returns a string
- Numeric operators: `+ - * / // %`
- Multiple assignment: `x, y, z = 1, 2, 3`

## Run it
```
python lesson01.py
```

## Exercise
Fill in the blanks at the bottom of `lesson01.py`:
1. `first_name` — your first name
2. `birth_year` — the year you were born (int)
3. `age_estimate` = `2026 - birth_year`
4. Print an f-string: `"Hi <first_name>, you are approximately <age_estimate> years old"`

## Status
- [ ] Exercise completed
