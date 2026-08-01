# Lesson 3: Functions

## Topics
- `def name(params):` (vs PowerShell `function name($params) { }`)
- Explicit `return` — Python does NOT auto-output like PowerShell does
- Default parameter values and keyword arguments
- Docstrings (`"""..."""` as the first line in the body) vs comment-based help
- `*args` (variable positional args, like `$args`) and `**kwargs` (variable named args)
- `lambda` — anonymous inline functions, vs PowerShell scriptblocks `{ }`

## Run it
```
python lesson03.py
```

## Exercise
At the bottom of `lesson03.py`:
1. `is_even(n)` — returns True/False
2. `describe_number(n)` — returns `"<n> is even"` or `"<n> is odd"`, using `is_even`
3. Loop `range(1, 6)` and print `describe_number(n)` for each

## Status
- [ ] Exercise completed
