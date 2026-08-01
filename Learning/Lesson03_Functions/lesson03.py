"""
SYNOPSIS
    Lesson 3: Functions - def, explicit return, default/keyword arguments,
    docstrings, *args/**kwargs, and lambda.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom.

EXAMPLE
    python lesson03.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

print("=" * 60)
print("LESSON 3: Functions")
print("=" * 60)

print("\n--- Basic function ---")
def greet(name):
    print(f"Hello {name}")

greet("Ruchik")

print("\n--- Return values ---")
# You must use `return` explicitly - nothing is auto-returned
def add(a, b):
    return a + b

result = add(3, 4)
print(result)

print("\n--- Default parameter values ---")
def greet_with(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet_with("Ruchik")
greet_with("Ruchik", "Hi")
greet_with(name="Ruchik", greeting="Hey")   # keyword args, order doesn't matter

print("\n--- Docstrings ---")
# a string literal as the FIRST line inside the function body
def multiply(a, b):
    """Returns the product of a and b."""
    return a * b

print(multiply.__doc__)

print("\n--- Variable number of arguments ---")
# *args collects extra positional args into a tuple
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3, 4))

# **kwargs collects extra named args into a dict
def show_info(**details):
    for key, value in details.items():
        print(f"{key}: {value}")

show_info(city="Zurich", country="Switzerland")

print("\n--- Lambda (anonymous function) ---")
square = lambda x: x * x
print(square(5))


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson03.py
# ============================================================
#
# 1. Write a function `is_even(n)` that returns True if n is even, False otherwise
# 2. Write a function `describe_number(n)` that returns the string:
#       "<n> is even" or "<n> is odd"    (use is_even inside it)
# 3. Loop over range(1, 6) and print describe_number(n) for each

# --- write your code below this line ---
