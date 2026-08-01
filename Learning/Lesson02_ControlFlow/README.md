# Lesson 2: Control Flow — if/else, loops, comparisons

## Topics
- No braces `{}` — indentation defines blocks, lines end with `:`
- `if` / `elif` / `else` (vs PowerShell `if` / `elseif` / `else`)
- Comparison operators: `== != < > <= >=` (plain symbols, not `-eq`/`-ne`/etc.)
- Logic operators: `and` / `or` / `not` (vs `-and`/`-or`/`-not`)
- `for i in range(n):` (vs `for ($i=0; $i -lt n; $i++)`)
- `for item in collection:` (vs `foreach ($item in $items)`)
- `enumerate()` for index + value together
- `while` loops, `+= 1` (no `++` operator in Python)
- `break` / `continue` — same keywords as PowerShell

## Run it
```
python lesson02.py
```

## Exercise
At the bottom of `lesson02.py`:
1. Create `scores = [55, 82, 91, 40, 67]`
2. Loop over it, printing `"FAIL"` (<60), `"PASS"` (60–79), or `"GREAT"` (>=80) per score
3. Track `great_count` for scores >= 80 and print it after the loop

## Status
- [ ] Exercise completed
