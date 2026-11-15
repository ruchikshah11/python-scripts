# Lesson 12: Regular Expressions in Python (`re` module)

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and interactive reference script covering Regular Expressions (regex) in Python using the built-in `re` module. Covers metacharacters, character classes, quantifiers, search methods (`search`, `match`, `fullmatch`, `findall`, `finditer`), string replacements with `re.sub()`, capturing and named groups, lookaround assertions, regex compilation (`re.compile`), and flags.

---

## 1. Introduction

A **Regular Expression** (regex) is a sequence of characters defining a search pattern. In Python, the standard library provides the `re` module, an efficient and powerful engine written in C.

Regex is essential in software engineering for:
- **Input Validation**: Verifying emails, telephone numbers, postal codes, and passwords.
- **Data Scraping & Extraction**: Isolating URLs, IP addresses, dates, or prices from raw unstructured text.
- **Log Parsing & Analysis**: Parsing server logs into structured JSON/dictionary objects.
- **String Cleaning & Reformatting**: Redacting sensitive PII or converting date/time formats.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain why **raw strings** (`r"..."`) must always be used with regular expressions in Python.
2. Differentiate between `re.match()`, `re.search()`, `re.fullmatch()`, `re.findall()`, and `re.finditer()`.
3. Use character classes (`\d`, `\w`, `\s`, custom sets `[...]`, and negated sets `[^...]`).
4. Apply quantifiers (`*`, `+`, `?`, `{n,m}`) and understand **Greedy vs. Non-Greedy (Lazy)** evaluation.
5. Extract structured data using numbered groups `(...)` and named groups `(?P<name>...)`.
6. Use non-capturing groups `(?:...)` for performance optimization.
7. Search and replace text with `re.sub()`, `re.subn()`, and function callbacks.
8. Optimize regex performance using `re.compile()` for repeated matching.
9. Use compilation flags: `re.IGNORECASE`, `re.MULTILINE`, `re.DOTALL`, and `re.VERBOSE`.
10. Implement zero-width **Lookaround Assertions** (Lookahead and Lookbehind).
11. Solve real-world parsing challenges and common technical interview questions.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Regex Mechanics](#4-core-regex-mechanics)
  - [4.1 Raw Strings in Python](#41-raw-strings-in-python)
  - [4.2 Search Functions Compared](#42-search-functions-compared)
  - [4.3 Metacharacters & Character Classes](#43-metacharacters--character-classes)
  - [4.4 Greedy vs. Lazy Quantifiers](#44-greedy-vs-lazy-quantifiers)
  - [4.5 Grouping & Named Groups](#45-grouping--named-groups)
  - [4.6 Substitution & re.sub](#46-substitution--resub)
  - [4.7 Compilation & Flags](#47-compilation--flags)
  - [4.8 Lookahead and Lookbehind Assertions](#48-lookahead-and-lookbehind-assertions)
- [5. Code Examples](#5-code-examples)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. Core Regex Mechanics

### 4.1 Raw Strings in Python
Always prefix regex pattern strings with `r` (e.g. `r"\d+\.\d+"`). 
Without `r`, Python treats `\` as a standard string escape character (e.g. `\n`, `\t`), requiring tedious double-escaping (`"\\d+\\.\\d+"`).

### 4.2 Search Functions Compared

| Function | What it does | Return Value |
| :--- | :--- | :--- |
| `re.search(pat, text)` | Scans through string looking for the **first** location where pattern matches | `Match` object or `None` |
| `re.match(pat, text)` | Checks for a match **only at the beginning** (index 0) of the string | `Match` object or `None` |
| `re.fullmatch(pat, text)` | Checks if the **entire string** matches the pattern from start to end | `Match` object or `None` |
| `re.findall(pat, text)` | Finds all occurrences of the pattern in the string | `list` of matching strings (or tuples of groups) |
| `re.finditer(pat, text)` | Finds all occurrences, returning an iterator of `Match` objects lazily | Iterator yielding `Match` objects |

### 4.3 Metacharacters & Character Classes

- `\d`: Any digit `[0-9]` | `\D`: Any non-digit `[^0-9]`
- `\w`: Any alphanumeric word character or underscore `[a-zA-Z0-9_]` | `\W`: Non-word character
- `\s`: Any whitespace `[ \t\n\r\f\v]` | `\S`: Non-whitespace
- `.`: Any character except newline (unless `re.DOTALL` flag is active)
- `^`: Start of string (or line with `re.MULTILINE`)
- `$`: End of string (or line with `re.MULTILINE`)
- `\b`: Word boundary | `\B`: Non-word boundary

### 4.4 Greedy vs. Lazy Quantifiers
- **Greedy** (`*`, `+`, `{n,m}`): Matches as many characters as possible.
- **Lazy / Non-Greedy** (`*?`, `+?`, `{n,m}?`): Matches as few characters as possible.

```python
html = "<p>First</p><p>Second</p>"
re.findall(r"<p>.*</p>", html)   # Greedy -> ['<p>First</p><p>Second</p>']
re.findall(r"<p>.*?</p>", html)  # Lazy   -> ['<p>First</p>', '<p>Second</p>']
```

### 4.5 Grouping & Named Groups
- **Numbered Groups**: `(\d{4})-(\d{2})` -> accessed via `match.group(1)`, `match.group(2)`.
- **Named Groups**: `(?P<year>\d{4})-(?P<month>\d{2})` -> accessed via `match.group('year')` or `match.groupdict()`.
- **Non-Capturing Groups**: `(?:https?://)?` -> groups without saving capture memory overhead.

### 4.6 Substitution & re.sub
- `re.sub(pattern, replacement, string)` replaces matches with a string or backreference (`\1`, `\g<name>`).
- You can pass a **callback function** to `re.sub` for dynamic transformations:
```python
re.sub(r"\b\w+\b", lambda m: m.group().upper(), "hello world")  # 'HELLO WORLD'
```

### 4.7 Compilation & Flags
Compiling with `re.compile()` stores regex bytecode in memory, avoiding recompilation when evaluated thousands of times in a loop.

Common flags:
- `re.IGNORECASE` (`re.I`): Case-insensitive matching.
- `re.MULTILINE` (`re.M`): `^` and `$` match at the start/end of each individual line.
- `re.DOTALL` (`re.S`): Makes `.` match newlines `\n` as well.
- `re.VERBOSE` (`re.X`): Allows formatted multi-line regex with inline whitespace and `# comments`.

### 4.8 Lookahead and Lookbehind Assertions
Zero-width assertions that match characters without consuming them or including them in the match result:

| Syntax | Type | Matches when... |
| :--- | :--- | :--- |
| `(?=pattern)` | Positive Lookahead | Followed by `pattern` |
| `(?!pattern)` | Negative Lookahead | NOT followed by `pattern` |
| `(?<=pattern)` | Positive Lookbehind | Preceded by `pattern` |
| `(?<!pattern)` | Negative Lookbehind | NOT preceded by `pattern` |

```python
# Match digits preceded by $:
re.findall(r"(?<=\$)\d+", "Apple $15, Orange 20")  # ['15']
```

---

## 5. Code Examples

All concepts are fully implemented and runnable in [regular_expressions.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson12_RegularExpressions/regular_expressions.py):
1. **Raw string demonstration**.
2. **Search methods comparison**: `match` vs. `search` vs. `fullmatch` vs. `findall` vs. `finditer`.
3. **Character classes & word boundaries**.
4. **Greedy vs. lazy matching on HTML tags**.
5. **Capturing & named groups with log parsing**.
6. **String substitution, backreferences & custom lambda callbacks**.
7. **Performance benchmarking with `re.compile()`**.
8. **Regex flags**: `IGNORECASE`, `MULTILINE`, `DOTALL`, and `VERBOSE`.
9. **Zero-width lookarounds & password strength verification**.
10. **Real-world IP and phone number regex matching**.

---

## 6. Frequently Asked Interview Questions

### Q1: What is the difference between `re.match()` and `re.search()`?
**Answer**:
- `re.match()` checks for a match **only at the beginning of the string** (index 0). If the pattern does not match the first character, it immediately returns `None`.
- `re.search()` scans the entire string from left to right and returns the first occurrence wherever it appears.

### Q2: Why should you prefer `re.finditer()` over `re.findall()` for large texts?
**Answer**:
`re.findall()` eagerly loads all matching strings into a new Python list in memory at once ($O(N)$ memory). `re.finditer()` returns a lazy iterator yielding `Match` objects one by one on demand ($O(1)$ memory), allowing access to `.span()`, `.start()`, and `.end()` without memory overhead.

### Q3: What is the purpose of raw strings (`r"..."`) in Python regex?
**Answer**:
Python standard string literals process escape sequences like `\n` (newline) or `\b` (backspace). Without `r"..."`, to match a literal backslash or regex boundary `\b`, you would have to write `"\\\\"` or `"\\b"`. A raw string passes the backslash directly to the regex engine without string pre-processing.

### Q4: How does a non-capturing group `(?:...)` differ from a capturing group `(...)`?
**Answer**:
A capturing group saves the matched substring into group memory (accessible via `m.group(1)` or `m.groups()`). A non-capturing group `(?:...)` applies quantifiers or alternation (`|`) to a subpattern without capturing it, saving execution time and memory.

### Q5: What are lookaround assertions and why don't they consume characters?
**Answer**:
Lookarounds (`(?=...)`, `(?!...)`, `(?<=...)`, `(?<!...)`) are **zero-width assertions**. They assert whether a condition matches immediately ahead or behind the current position, but they do not advance the engine's match pointer or include the inspected characters in the resulting match string.

---

## 7. How to Run

Run the lesson script directly from terminal:
```bash
python regular_expressions.py
```

---

## 8. Exercises

At the bottom of [regular_expressions.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson12_RegularExpressions/regular_expressions.py):
1. **Email Validator**: Write `is_valid_email(email)` verifying username, `@`, domain, and 2-6 character TLD.
2. **Date Reformatting**: Use `re.sub()` to convert `"YYYY/MM/DD"` dates into `"DD-MM-YYYY"` format.
3. **Log Parser**: Parse a structured log line using named groups `(?P<severity>)`, `(?P<timestamp>)`, `(?P<service>)`, and `(?P<message>)`.
4. **Word Boundary Frequency**: Extract all words and count occurrences of the whole word `"python"` case-insensitively using `\b` and `re.findall()`.
5. **Lookaround Extraction**: Extract only numerical amounts representing monetary dollar values preceded by `$` using positive lookbehind.

---

## 9. Completion Checklist

- [ ] Run `python regular_expressions.py` and inspect all outputs.
- [ ] Understand the difference between `re.match()`, `re.search()`, and `re.fullmatch()`.
- [ ] Implement exercise 1 (Email validator).
- [ ] Implement exercise 2 (Date reformatting with `re.sub`).
- [ ] Implement exercise 3 (Log parsing with named groups).
- [ ] Implement exercise 4 (Word boundary counting).
- [ ] Implement exercise 5 (Zero-width lookbehind).
- [ ] Review all interview questions and answers.
