"""
SYNOPSIS
    Lesson 16: Lambda and Functional Programming in Python - Anonymous functions
    (lambda syntax and limitations), map(), filter(), functools.reduce(),
    sorted() with key=lambda, max()/min() with custom keys, closures,
    currying/partial functions (functools.partial), list/dict comprehensions
    vs map/filter, and practical clean functional patterns.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python lambda_and_functional.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

from functools import reduce, partial

print("=" * 60)
print("LESSON 16: Lambda and Functional Programming in Python")
print("=" * 60)


# ============================================================
# 1. Lambda Functions: Syntax & Comparison with def
# ============================================================
print("\n--- 1. Lambda Syntax vs Standard def ---")
# Syntax: lambda parameter_list: expression
# A lambda is an anonymous, inline function restricted to a single expression.
# The expression is automatically evaluated and returned (no 'return' keyword allowed).

# Standard function
def add_standard(a: int, b: int) -> int:
    return a + b

# Equivalent lambda function
add_lambda = lambda a, b: a + b

print(f"add_standard(10, 5) : {add_standard(10, 5)}")
print(f"add_lambda(10, 5)   : {add_lambda(10, 5)}")
print(f"Type of add_lambda  : {type(add_lambda).__name__} (name: '{add_lambda.__name__}')")


# ============================================================
# 2. Sorting with Custom Keys (sorted & list.sort)
# ============================================================
print("\n--- 2. Sorting Collections with Custom Lambda Keys ---")
# The most common, idiomatic use case for lambda in Python is the `key=` parameter.

users = [
    {"name": "Navneet", "score": 95, "age": 28},
    {"name": "Sara", "score": 88, "age": 24},
    {"name": "Vikram", "score": 95, "age": 22},
    {"name": "Maya", "score": 79, "age": 31},
]

# Sort by score descending
by_score = sorted(users, key=lambda u: u["score"], reverse=True)
print("Users sorted by score (descending):")
for u in by_score:
    print(f"  {u['name']}: {u['score']}")

# Multi-level sorting: Primary sort by score DESC, secondary tie-breaker by age ASC
multi_sort = sorted(users, key=lambda u: (-u["score"], u["age"]))
print("Users sorted by score DESC, then age ASC:")
for u in multi_sort:
    print(f"  {u['name']}: score={u['score']}, age={u['age']}")

# min() and max() with custom key
top_performer = max(users, key=lambda u: u["score"])
print(f"Top performer: {top_performer['name']} ({top_performer['score']} pts)")


# ============================================================
# 3. Higher-Order Functions: map() and filter()
# ============================================================
print("\n--- 3. Higher-Order Functions: map() and filter() ---")
# map(func, iterable): transforms each element lazily
# filter(func, iterable): retains elements where func(x) evaluates to True

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map with lambda: square each number
squared = list(map(lambda x: x ** 2, numbers))
print(f"Original numbers: {numbers}")
print(f"map(x**2)       : {squared}")

# filter with lambda: keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"filter(even)    : {evens}")

# Chaining filter and map
even_squares = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
print(f"Evens squared   : {even_squares}")

# Pythonic alternative: List comprehensions are generally preferred over map/filter for readability
list_comp_equivalent = [x ** 2 for x in numbers if x % 2 == 0]
print(f"List comprehension equivalent: {list_comp_equivalent}")


# ============================================================
# 4. Aggregation with functools.reduce()
# ============================================================
print("\n--- 4. Aggregation with functools.reduce() ---")
# reduce(func, sequence): repeatedly applies func to pairs of elements
# from left to right to reduce the sequence to a single cumulative value.

nums = [1, 2, 3, 4, 5]

# Calculate product: (((1 * 2) * 3) * 4) * 5
product = reduce(lambda acc, x: acc * x, nums)
print(f"Product of {nums} via reduce: {product}")

# Find maximum value in a list using reduce
max_val = reduce(lambda a, b: a if a > b else b, [14, 82, 35, 99, 41])
print(f"Max value via reduce: {max_val}")


# ============================================================
# 5. Closures & Function Factories with Lambda
# ============================================================
print("\n--- 5. Closures & Function Factories ---")


def make_multiplier(factor: float):
    """Returns a lambda that captures factor in its closure."""
    return lambda x: x * factor


double = make_multiplier(2)
triple = make_multiplier(3)

print(f"double(21): {double(21)}")
print(f"triple(21): {triple(21)}")


# ============================================================
# 6. Partial Functions (functools.partial)
# ============================================================
print("\n--- 6. Partial Functions (functools.partial) ---")
# partial freezes a portion of a function's arguments, producing a new callable


def power(base: float, exponent: float) -> float:
    return base ** exponent


square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(f"square(9): {square(9)}")
print(f"cube(3)  : {cube(3)}")


# ============================================================
# 7. Common Pitfall: Late Binding in Closures / Loops
# ============================================================
print("\n--- 7. Common Pitfall: Late Binding in Closures ---")
# In Python, closures capture variables by reference, not by value at creation time.

# BROKEN: all lambdas capture the final value of 'i' (which is 2)
broken_funcs = [lambda: i for i in range(3)]
print(f"Late binding (broken) : {[f() for f in broken_funcs]} (all return 2!)")

# FIXED: use default argument binding `lambda i=i:` to freeze the value at definition time
fixed_funcs = [lambda i=i: i for i in range(3)]
print(f"Default binding (fixed): {[f() for f in fixed_funcs]} (returns 0, 1, 2)")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lambda_and_functional.py
# ============================================================
#
# 1. INLINE STRING TRANSFORMATION:
#    Given words = ["apple", "banana", "kiwi", "strawberry", "fig"]
#    Sort the words primarily by string length ASC, and secondarily in alphabetical order.
#
# 2. FILTER & MAP PIPELINE:
#    Given temperatures_c = [-5, 0, 15, 22, 35, 40, -1]
#    Use `filter()` to select temperatures strictly above 0°C, then use `map()`
#    to convert them to Fahrenheit: `F = (C * 9/5) + 32`.
#
# 3. REDUCE AGGREGATOR:
#    Use `functools.reduce` to concatenate a list of strings `["Functional", "Programming", "With", "Python"]`
#    into a single hyphen-separated string: `"Functional-Programming-With-Python"`.
#
# 4. PARTIAL DISCOUNT APPLIER:
#    Write a base function `apply_discount(price, discount_percent)`.
#    Create a `black_friday_discount` partial function with `discount_percent=30`.
#    Calculate the discounted price for a $200.00 item.

# --- write your code below this line ---
