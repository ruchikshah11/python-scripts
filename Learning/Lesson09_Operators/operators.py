"""
SYNOPSIS
    Reference and demo of Python's operators - arithmetic, comparison, logical,
    bitwise, assignment (including augmented and walrus), identity, and
    membership operators, plus a note on precedence.

DESCRIPTION
    Run this file top-to-bottom to see every operator's output, then use it
    as a reference later.

EXAMPLE
    python operators.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

print("=" * 60)
print("LESSON 9: Operators")
print("=" * 60)

print("\n--- Arithmetic operators ---")
a, b = 17, 5
print(f"a = {a}, b = {b}")
print(f"a + b = {a + b}")    # addition
print(f"a - b = {a - b}")    # subtraction
print(f"a * b = {a * b}")    # multiplication
print(f"a / b = {a / b}")    # true division - always returns a float
print(f"a // b = {a // b}")  # floor division - rounds down to the nearest whole number
print(f"a % b = {a % b}")    # modulo - remainder after division
print(f"a ** b = {a ** b}")  # exponentiation - a to the power of b
print(f"-a = {-a}")          # unary minus


print("\n--- Comparison operators ---")
x, y = 10, 20
print(f"x == y = {x == y}")  # equal to
print(f"x != y = {x != y}")  # not equal to
print(f"x > y = {x > y}")    # greater than
print(f"x < y = {x < y}")    # less than
print(f"x >= 10 = {x >= 10}")  # greater than or equal to
print(f"x <= 10 = {x <= 10}")  # less than or equal to
print(f"1 < 2 < 3 = {1 < 2 < 3}")  # chained comparison - Python-specific, equivalent to (1 < 2) and (2 < 3)


print("\n--- Logical operators ---")
is_admin = True
is_active = False
print(f"is_admin and is_active = {is_admin and is_active}")  # True only if BOTH are true
print(f"is_admin or is_active = {is_admin or is_active}")    # True if EITHER is true
print(f"not is_admin = {not is_admin}")                       # inverts the value
# short-circuit evaluation: the right side is only evaluated if needed
print(f"False and (1 / 0 == 0) -> {False and False}")   # right side never actually runs here


print("\n--- Bitwise operators (operate on the binary representation of ints) ---")
p, q = 12, 10   # 12 = 0b1100, 10 = 0b1010
print(f"p & q = {p & q}")    # AND  - bits set in both
print(f"p | q = {p | q}")    # OR   - bits set in either
print(f"p ^ q = {p ^ q}")    # XOR  - bits set in exactly one
print(f"~p = {~p}")          # NOT  - inverts all bits (equivalent to -p - 1)
print(f"p << 2 = {p << 2}")  # left shift  - multiplies by 2 per shift
print(f"p >> 2 = {p >> 2}")  # right shift - divides by 2 per shift (floor)


print("\n--- Assignment operators ---")
n = 10
print(f"n = {n}")
n += 5   # same as n = n + 5
print(f"n += 5 -> {n}")
n -= 3
print(f"n -= 3 -> {n}")
n *= 2
print(f"n *= 2 -> {n}")
n /= 4
print(f"n /= 4 -> {n}")
n //= 2
print(f"n //= 2 -> {n}")
n **= 2
print(f"n **= 2 -> {n}")
n %= 5
print(f"n %= 5 -> {n}")
m = 6
m &= 3
print(f"m = 6; m &= 3 -> {m}")
m |= 8
print(f"m |= 8 -> {m}")
m ^= 2
print(f"m ^= 2 -> {m}")
m <<= 1
print(f"m <<= 1 -> {m}")
m >>= 2
print(f"m >>= 2 -> {m}")

# Walrus operator (:=, Python 3.8+) - assigns AND returns a value in one expression,
# most useful inside a condition or comprehension to avoid computing something twice
values = [1, 2, 3, 4, 5]
if (count := len(values)) > 3:
    print(f"walrus: count := len(values) -> {count} (> 3, so this branch ran)")


print("\n--- Identity operators (is / is not) - compare OBJECT IDENTITY, not value ---")
list_a = [1, 2, 3]
list_b = [1, 2, 3]
list_c = list_a
print(f"list_a == list_b = {list_a == list_b}")  # True - same VALUES
print(f"list_a is list_b = {list_a is list_b}")   # False - different objects in memory
print(f"list_a is list_c = {list_a is list_c}")   # True - list_c points to the SAME object
print(f"list_a is not list_b = {list_a is not list_b}")


print("\n--- Membership operators (in / not in) ---")
fruits = ["apple", "banana", "cherry"]
print(f"'banana' in fruits = {'banana' in fruits}")
print(f"'mango' in fruits = {'mango' in fruits}")
print(f"'mango' not in fruits = {'mango' not in fruits}")
print(f"'a' in 'banana' = {'a' in 'banana'}")  # works on strings too - substring/character check


print("\n--- Operator precedence (a quick reminder, highest to lowest of the above) ---")
# ** > unary +/-/~ > * / // % > + - > << >> > & > ^ > | > comparisons > not > and > or
print(f"2 + 3 * 4 = {2 + 3 * 4}")        # 14, not 20 - * runs before +
print(f"(2 + 3) * 4 = {(2 + 3) * 4}")    # 20 - parentheses always win, use them when unsure
print(f"2 ** 3 ** 2 = {2 ** 3 ** 2}")     # 512 - ** is right-associative: 2 ** (3 ** 2), not (2 ** 3) ** 2


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python operators.py
# ============================================================
#
# 1. Given `price = 49.99` and `quantity = 3`, compute the total using `*`,
#    then use `//` and `%` to show how many whole "$10 notes" it would take
#    to pay it and what remainder (in cents, rounded) would be left.
# 2. Given `flags = 0`, use `|=` to set bit 0 and bit 2 (i.e. add 1 and 4),
#    then use `&` to check whether bit 1 (value 2) is set.
# 3. Given `a = [1, 2]` and `b = a`, and `c = [1, 2]`, print the results of
#    `a is b`, `a is c`, and `a == c`, and make sure you can explain why
#    each one is what it is.
# 4. Using the walrus operator, write a loop that reads from a list of
#    numbers `data = [4, 8, 15, 16, 23, 42]` and stops printing as soon as
#    a running total (assigned via `:=`) exceeds 30.

# --- write your code below this line ---
