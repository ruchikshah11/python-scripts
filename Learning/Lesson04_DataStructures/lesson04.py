"""
SYNOPSIS
    Lesson 4: Data Structures - list (indexing, slicing, comprehensions),
    tuple, dict, set, and nested structures.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercise at the bottom.

EXAMPLE
    python lesson04.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

print("=" * 60)
print("LESSON 4: Data Structures")
print("=" * 60)

print("\n--- List ---")
fruits = ["apple", "banana", "cherry"]
print(fruits[0])          # apple  - indexing
print(fruits[-1])         # cherry - negative index = from the end
fruits.append("date")
print(fruits)
print(len(fruits))

print("\n--- Slicing ---")
print(fruits[1:3])        # ["banana", "cherry"]  - index 1 up to (not including) 3

print("\n--- List comprehension ---")
upper_fruits = [f.upper() for f in fruits]
print(upper_fruits)

print("\n--- Tuple (immutable list - fixed once created) ---")
point = (10, 20)
print(point[0], point[1])
# point[0] = 99   # <- this would raise an error, tuples can't be changed

print("\n--- Dict ---")
person = {
    "name": "Ruchik",
    "age": 27,
    "city": "Zurich"
}
print(person["name"])
person["role"] = "Consultant"
print(person)

for key, value in person.items():
    print(f"{key}: {value}")

print(person.keys())
print(person.values())
print("age" in person)

print("\n--- Set (unique values only, no duplicates) ---")
numbers = [1, 2, 2, 3, 3, 3]
unique_numbers = set(numbers)
print(unique_numbers)   # {1, 2, 3}

print("\n--- Nested structures (very common - e.g. parsed JSON) ---")
people = [
    {"name": "Ruchik", "age": 27},
    {"name": "Kalpesh", "age": 30},
]
for p in people:
    print(f"{p['name']} is {p['age']}")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson04.py
# ============================================================
#
# 1. Create a list `names` = ["Alice", "Bob", "Charlie", "Dave"]
# 2. Create a dict `ages` mapping each name to an age of your choice
# 3. Loop over `names` and print "<name> is <age>" using the `ages` dict
# 4. Use a list comprehension to build `short_names` containing only names
#    with 5 or fewer letters, then print it

# --- write your code below this line ---
