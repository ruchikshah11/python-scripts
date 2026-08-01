# Lesson 4: Data Structures

## Topics
- `list` — like a PowerShell array `@()`: indexing, negative indexing, `.append()`, slicing
- List comprehensions: `[expr for item in list]`
- `tuple` — immutable, fixed-size list
- `dict` — like a PowerShell hashtable `@{}`: `.items()`, `.keys()`, `.values()`, `in` for key check
- `set` — unique values only, no duplicates
- Nesting dicts/lists together (e.g. shape of parsed JSON)

## Run it
```
python lesson04.py
```

## Exercise
At the bottom of `lesson04.py`:
1. `names = ["Alice", "Bob", "Charlie", "Dave"]`
2. `ages` dict mapping each name to an age
3. Loop `names`, print `"<name> is <age>"` via the `ages` dict
4. List comprehension `short_names` — names with <= 5 letters

## Status
- [ ] Exercise completed
