"""
SYNOPSIS
    Lesson 1: Variables, Types, and Basic I/O - variables, types, f-strings,
    print()/input(), and numeric operators.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom.

EXAMPLE
    python lesson01.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

print("=" * 60)
print("LESSON 1: Variables, Types, and Basic I/O")
print("=" * 60)

print("\n--- Variables ---")
name = "Ruchik"
age = 27
is_admin = True

print("\n--- Types ---")
print(type(name).__name__)   # str
print(type(age).__name__)    # int
print(type(is_admin).__name__)  # bool

print("\n--- String formatting ---")
# f-string: prefix the quote with f, embed variables directly inside {}
print(f"Hello {name}, you are {age}")

print("\n--- Output ---")
print("This prints to the console")

print("\n--- Input ---")
# input() always returns a string - convert with int()/float() if you need a number
city = input("Enter your city: ")
print(f"You live in {city}")

print("\n--- Numbers & operators ---")
a = 10
b = 3
print(f"Mathmatical operations with a={a} and b={b}:")
print(a + b)   # 13
print(a - b)   # 7
print(a * b)   # 30
print(a / b)   # 3.333... -> "/" always gives a float
print(a // b)  # 3        -> "//" is integer (floor) division
print(a % b)   # 1        -> modulo

print("\n--- Multiple assignment ---")
x, y, z = 1, 2, 3
print(x, y, z)


# ============================================================
# EXERCISE - fill in the blanks below, then run:
#     python lesson01.py
# ============================================================

# 1. Create a variable `first_name` with your first name
# 2. Create a variable `birth_year` with the year you were born (as an int)
# 3. Calculate `age_estimate` = 2026 - birth_year
# 4. Print an f-string: "Hi <first_name>, you are approximately <age_estimate> years old"

# --- write your code below this line ---
