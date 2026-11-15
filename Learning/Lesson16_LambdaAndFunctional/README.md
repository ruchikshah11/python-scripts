# Lesson 16: Lambda and Functional Programming in Python

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script exploring Python's functional programming capabilities: anonymous `lambda` expressions, custom sorting keys, higher-order functions (`map`, `filter`, `reduce`), closures, currying with `functools.partial`, and common pitfalls like late binding in loops.

---

## 1. Introduction

Functional programming emphasizes evaluating pure functions and avoiding mutable state. In Python, while multi-paradigm, functional constructs like `lambda`, `map`, `filter`, and `functools` provide concise, elegant solutions for data transformation pipelines.

A `lambda` expression in Python is a lightweight, anonymous function defined inline without a name or a `def` block.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Master the syntax and limitations of `lambda` functions (`lambda args: expression`).
2. Use lambdas for custom collection sorting (`key=lambda x: ...`) including multi-level tie-breakers.
3. Transform and filter streams with `map()` and `filter()`.
4. Aggregate sequences using `functools.reduce()`.
5. Create function factories and closures using lambdas.
6. Freeze function arguments using `functools.partial`.
7. Avoid the infamous **late binding** closure bug in Python loops.
8. Distinguish when to use `lambda` vs. `def` vs. list comprehensions.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Functional Concepts](#4-core-functional-concepts)
  - [4.1 Lambda Syntax and Limitations](#41-lambda-syntax-and-limitations)
  - [4.2 Custom Sorting Keys with `sorted()`](#42-custom-sorting-keys-with-sorted)
  - [4.3 `map()` and `filter()`](#43-map-and-filter)
  - [4.4 Aggregation with `reduce()`](#44-aggregation-with-reduce)
  - [4.5 Partial Functions (`functools.partial`)](#45-partial-functions-functoolspartial)
  - [4.6 Late Binding in Closures](#46-late-binding-in-closures)
- [5. Frequently Asked Interview Questions](#5-frequently-asked-interview-questions)
- [6. How to Run](#6-how-to-run)
- [7. Exercises](#7-exercises)
- [8. Completion Checklist](#8-completion-checklist)

---

## 4. Core Functional Concepts

### 4.1 Lambda Syntax and Limitations
```python
# Syntax: lambda parameter_list: expression
multiply = lambda x, y: x * y
```
**Limitations**:
- Restricted strictly to a **single expression**.
- Statements like `return`, `pass`, `assert`, or assignments (`=`) are forbidden inside a lambda body.
- No docstrings or explicit type annotations in the header.

### 4.2 Custom Sorting Keys with `sorted()`
The most Pythonic use case for `lambda` is as an inline sorting key:
```python
users = [{"name": "Navneet", "score": 95}, {"name": "Sara", "score": 88}]
# Sort by score descending:
sorted(users, key=lambda u: u["score"], reverse=True)
```

### 4.3 `map()` and `filter()`
- `map(func, iterable)`: Lazily applies `func` to every item in the iterable.
- `filter(func, iterable)`: Lazily yields items for which `func(item)` is truthy.
```python
evens = filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5, 6])
squares = map(lambda x: x ** 2, evens)
```

### 4.4 Aggregation with `reduce()`
`functools.reduce(func, iterable)` applies a function cumulatively:
```python
from functools import reduce

nums = [1, 2, 3, 4, 5]
total_sum = reduce(lambda acc, x: acc + x, nums)  # 15
```

### 4.5 Partial Functions (`functools.partial`)
Pre-binds arguments to create specialized functions:
```python
from functools import partial

def power(base, exp): return base ** exp
square = partial(power, exp=2)
square(10)  # 100
```

### 4.6 Late Binding in Closures
Python closures look up variables when the function is **called**, not when it is created.
```python
# BROKEN: all 3 lambdas return 2 (final value of i)
funcs = [lambda: i for i in range(3)]

# FIXED: bind i to default argument at definition time
funcs = [lambda i=i: i for i in range(3)]  # returns 0, 1, 2
```

---

## 5. Frequently Asked Interview Questions

### Q1: What is the difference between a normal function (`def`) and a lambda?
**Answer**:
A standard function (`def`) can contain multiple expressions, control flow statements (`if/else`, loops, `try/except`), local variable assignments, docstrings, and type annotations. A `lambda` is an anonymous function restricted to a single evaluated expression that implicitly returns its value.

### Q2: Why are list comprehensions generally preferred over `map()` and `filter()` in Python?
**Answer**:
List comprehensions are typically faster because they avoid function call overhead for every element, and they are widely considered more readable in idiomatic Python:
```python
# Comprehension (Clear & Pythonic)
[x * 2 for x in nums if x > 0]

# map + filter + lambda (Verbose)
map(lambda x: x * 2, filter(lambda x: x > 0, nums))
```

### Q3: How do you fix late-binding variables in a lambda created inside a loop?
**Answer**:
Pass the loop variable as a default argument in the lambda signature: `lambda i=i: i`. Since default arguments are evaluated when the function definition is executed, the current loop value is permanently bound to that instance.

---

## 6. How to Run

Run the script from your terminal:
```bash
python lambda_and_functional.py
```

---

## 7. Exercises

In [lambda_and_functional.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson16_LambdaAndFunctional/lambda_and_functional.py):
1. **Multi-level Sorting**: Sort a list of strings by length ASC, then alphabetically.
2. **Temperature Pipeline**: Filter Celsius temperatures above 0°C and map them to Fahrenheit.
3. **String Join with Reduce**: Use `functools.reduce` to create a hyphenated slug from a word list.
4. **Partial Discount Calculator**: Create a specialized partial function with `discount_percent=30`.

---

## 8. Completion Checklist

- [ ] Run `python lambda_and_functional.py` and inspect all outputs.
- [ ] Understand lambda syntax and limits.
- [ ] Complete exercise 1 (Multi-level custom key sort).
- [ ] Complete exercise 2 (Filter & map pipeline).
- [ ] Complete exercise 3 (Reduce aggregator).
- [ ] Complete exercise 4 (functools.partial).
- [ ] Review all interview questions.
