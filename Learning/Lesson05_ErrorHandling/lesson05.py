"""
SYNOPSIS
    Lesson 5: Error Handling - try/except/else/finally, raising exceptions
    with raise, and custom exception classes.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom.

EXAMPLE
    python lesson05.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

print("=" * 60)
print("LESSON 5: Error Handling")
print("=" * 60)

print("\n--- Basic try/except ---")
try:
    result = 10 / 0
except ZeroDivisionError as ex:
    print(f"Error: {ex}")

print("\n--- Catching a specific type ---")
try:
    with open("does_not_exist.txt") as f:
        content = f.read()
except FileNotFoundError as ex:
    print(f"File missing: {ex}")
except Exception as ex:
    # Generic catch-all for anything else
    print(f"Unexpected error: {ex}")

print("\n--- else and finally ---")
# `else` runs only if NO exception occurred
# `finally` always runs
try:
    value = int("42")
except ValueError as ex:
    print(f"Conversion failed: {ex}")
else:
    print(f"Conversion succeeded: {value}")
finally:
    print("This always runs")

print("\n--- Raising exceptions ---")
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age

try:
    set_age(-5)
except ValueError as ex:
    print(f"Caught: {ex}")

print("\n--- Custom exception ---")
class InsufficientFundsError(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(f"Cannot withdraw {amount}, balance is only {balance}")
    return balance - amount

try:
    withdraw(100, 150)
except InsufficientFundsError as ex:
    print(f"Transaction failed: {ex}")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson05.py
# ============================================================
#
# 1. Write a function `safe_divide(a, b)` that:
#    - returns a / b
#    - if b is 0, catches ZeroDivisionError internally and returns None instead
# 2. Call it with safe_divide(10, 2) and safe_divide(10, 0), printing both results
# 3. Write a function `validate_age(age)` that raises ValueError if age > 150 or age < 0,
#    otherwise returns age. Call it in a try/except with an invalid value (e.g. 200)
#    and print a friendly error message when it's caught.

# --- write your code below this line ---
