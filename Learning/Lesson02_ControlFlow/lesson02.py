"""
SYNOPSIS
    Lesson 2: Control Flow - if/elif/else, comparison and logic operators,
    for/while loops, enumerate(), break/continue. Python has no braces {} for
    blocks - indentation IS the block, and a line starting one ends with ":"

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom.

EXAMPLE
    python lesson02.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

print("=" * 60)
print("LESSON 2: Control Flow")
print("=" * 60)

print("\n--- if / elif / else ---")
age = 27
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")

print("\n--- Comparison & logic operators ---")
# comparisons: ==  !=  <  >  <=  >=
# logic:       and  or  not
is_admin = True
is_active = True
if is_admin and is_active:
    print("Admin and active")
if not is_admin:
    print("Not admin")

print("\n--- for loop over a range ---")
# range(5) generates 0,1,2,3,4 (stop value excluded)
for i in range(5):
    print(f"i = {i}")

print("\n--- for loop over a collection ---")
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

print("\n--- enumerate() (index + value together) ---")
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

print("\n--- while loop ---")
count = 0
while count < 3:
    print(f"count is {count}")
    count += 1   # Python has no ++ operator - use += 1

print("\n--- break / continue ---")
for n in range(10):
    if n == 3:
        continue   # skip this iteration
    if n == 6:
        break      # exit the loop entirely
    print(f"n = {n}")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson02.py
# ============================================================
#
# 1. Create a list `scores` = [55, 82, 91, 40, 67]
# 2. Loop over it, and for each score print:
#       - "FAIL" if score < 60
#       - "PASS" if 60 <= score < 80
#       - "GREAT" if score >= 80
# 3. Also count how many scores are >= 80 using a variable `great_count`,
#    and print it after the loop.

# --- write your code below this line ---
