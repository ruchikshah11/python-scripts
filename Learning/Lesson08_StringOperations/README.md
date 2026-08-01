# Lesson 8: String Operations

Reference and demo script covering **all 47** of Python's built-in string methods
(everything in `dir(str)`). Strings are **immutable** in Python — every method below
that looks like it "changes" a string actually returns a brand new one; the original is
never modified.

## Topics
- **Creating strings** — single/double/triple quotes, raw strings (`r"..."`), f-strings, byte strings (`b"..."`)
- **Length, indexing, slicing** — `len()`, `text[0]`, negative indices, `text[start:end]`, `text[::-1]` (reverse)
- **Concatenation & repetition** — `+`, `*`
- **Case conversion** — `.upper()`, `.lower()`, `.title()`, `.capitalize()`, `.swapcase()`, `.casefold()`
- **Searching & checking** — `.find()`, `.index()`, `.rfind()`, `.rindex()`, `.count()`, `.startswith()`, `.endswith()`, the `in` operator
- **Trimming** — `.strip()`, `.lstrip()`, `.rstrip()` (whitespace by default, or a specific character)
- **Splitting & joining** — `.split()`, `.rsplit()`, `.splitlines()`, `.partition()`, `.rpartition()`, `"sep".join(list)`
- **Replacing** — `.replace()` (with an optional count limit), `.removeprefix()`, `.removesuffix()` (3.9+)
- **Formatting** — f-strings, `.format()`, positional `.format()`, `.format_map()`, `%`-style (legacy), number formatting (`.2f`, zero-padding)
- **Padding & alignment** — `.ljust()`, `.rjust()`, `.center()`, `.zfill()`, `.expandtabs()`
- **Type checks** — `.isalpha()`, `.isdigit()`, `.isdecimal()`, `.isnumeric()`, `.isalnum()`, `.isspace()`, `.isupper()`, `.islower()`, `.istitle()`, `.isidentifier()`, `.isascii()`, `.isprintable()`
- **Encoding/decoding** — `.encode()`, `.decode()`
- **Translation** — `str.maketrans()` + `.translate()` for bulk character replacement
- **Membership & comparison** — `in`, lexicographic (`<`/`>`) comparison

## Run it
```
python string_operations.py
```

## Exercise
At the bottom of `string_operations.py`:
1. Trim + lowercase `"  Hello, PYTHON World!  "` using only string methods
2. Count occurrences of `"ain"` in `"the rain in spain falls mainly on the plain"`
3. Split `"Ruchik,27,Zurich"` then rejoin as `"Ruchik | 27 | Zurich"` using `join()`
4. Check whether `"user_id_42"` is a valid identifier with `.isidentifier()`

## Status
- [ ] Exercise completed
