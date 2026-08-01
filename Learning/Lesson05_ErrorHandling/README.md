# Lesson 5: Error Handling

## Topics
- `try` / `except` / `else` / `finally` (vs PowerShell `try` / `catch` / `finally`)
- Catching specific exception types vs a generic catch-all
- `else` block — runs only when no exception occurred (no direct PS equivalent)
- Raising errors: `raise ValueError("...")` (vs PowerShell `throw "..."`)
- Custom exception classes (`class MyError(Exception): pass`)

## Run it
```
python lesson05.py
```

## Exercise
At the bottom of `lesson05.py`:
1. `safe_divide(a, b)` — returns `a / b`, or `None` if `b == 0` (catch `ZeroDivisionError`)
2. Call it with `(10, 2)` and `(10, 0)`, print both results
3. `validate_age(age)` — raises `ValueError` if `age > 150` or `age < 0`, else returns `age`.
   Call with an invalid value inside a `try/except` and print a friendly message.

## Status
- [ ] Exercise completed
