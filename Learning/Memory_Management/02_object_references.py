"""
================================================================================
Topic 2: Object References, Identity, and Mutability
================================================================================

SYNOPSIS:
    Explores how Python variables work as name-tags (pointers) bound to objects
    rather than boxes holding values. Demonstrates object identity with id() and
    'is' vs '==', shared references, aliasing, and the deep impact of mutability.

CONCEPTS COVERED:
    1. Variables as Named References (The "Sticky Note" mental model).
    2. Object Identity using id() and the 'is' vs '==' comparison.
    3. Shared References and Aliasing.
    4. Mutable vs Immutable Objects in Memory.
    5. CPython Caching Optimizations: Small Integer Caching (-5 to 256) & String Interning.
    6. Common Pitfalls: In-place modifications and default mutable arguments.

EXPECTED OUTPUT HIGHLIGHTS:
    - Identical memory addresses for shared references and cached integers.
    - Divergent memory addresses for newly allocated mutable structures.
    - Side-effects of unintended aliasing mutations.
================================================================================
"""

import sys

print("=" * 70)
print("TOPIC 2: Object References, Identity, and Mutability")
print("=" * 70)


# ==============================================================================
# SECTION 1: Variables as References (Sticky Notes, Not Boxes)
# ==============================================================================
print("\n--- 1. Variables as Named References ---")
"""
In C/C++, a variable is a named memory location (a "box") that holds a value:
    int x = 10; // 'x' is a 4-byte slot in memory holding binary 10.

In Python, a variable is a REFERENCE (a "sticky label") attached to an object on the heap:
    x = 10     // Creates integer object 10 on heap; binds name 'x' to its address.
"""

a = [10, 20, 30]
b = a  # 'b' does NOT copy the list! 'b' binds to the EXACT SAME object in memory.

print(f"a points to address: {hex(id(a))} (value: {a})")
print(f"b points to address: {hex(id(b))} (value: {b})")
print(f"Are 'a' and 'b' pointing to the same object? -> {a is b}")


# ==============================================================================
# SECTION 2: Object Identity: id() and 'is' vs '=='
# ==============================================================================
print("\n--- 2. Object Identity: id() and 'is' vs '==' ---")
"""
- id(obj): Returns the unique integer identifier for an object.
  In CPython, id(obj) is the ACTUAL MEMORY ADDRESS of the PyObject struct in C!
- '==' (Equality): Calls obj.__eq__(); checks if two objects have the same VALUE/CONTENTS.
- 'is' (Identity): Compares pointers directly (id(a) == id(b)); checks if they are the EXACT SAME object.
"""

list1 = [1, 2, 3]
list2 = [1, 2, 3]

print(f"list1: {list1} at {hex(id(list1))}")
print(f"list2: {list2} at {hex(id(list2))}")
print(f"list1 == list2 : {list1 == list2} (Same contents)")
print(f"list1 is list2 : {list1 is list2} (Different objects in memory)")


# ==============================================================================
# SECTION 3: Shared References & The Aliasing Trap
# ==============================================================================
print("\n--- 3. Shared References & The Aliasing Trap ---")
"""
When multiple variable names point to the same MUTABLE object, modifying through
one name alters the object for ALL references!
"""

original = ["alpha", "beta"]
alias = original  # Shared reference

print(f"Before mutation: original={original}, alias={alias}")
alias.append("gamma")  # In-place modification
print(f"After alias.append('gamma'):")
print(f"  original: {original} (MUTATED!)")
print(f"  alias   : {alias}")


# ==============================================================================
# SECTION 4: Mutable vs Immutable Objects in Memory
# ==============================================================================
print("\n--- 4. Mutable vs Immutable Objects ---")
"""
IMMUTABLE: int, float, bool, str, tuple, frozenset, bytes.
  Once created in memory, their state CANNOT be changed.
  Operations that seem to modify them actually allocate a BRAND NEW object.

MUTABLE: list, dict, set, bytearray, custom classes.
  Their contents can be modified in-place at the same memory address.
"""

# Experiment with Immutable (integer reassignment):
x = 500
addr_before = id(x)
x += 1  # Allocates a new integer 501 on the heap
addr_after = id(x)
print(f"Immutable integer modification:")
print(f"  x before (500): address={hex(addr_before)}")
print(f"  x after  (501): address={hex(addr_after)} (Address CHANGED! Brand new object allocated)")

# Experiment with Mutable (list append):
nums = [1, 2]
addr_list_before = id(nums)
nums.append(3)
addr_list_after = id(nums)
print(f"Mutable list modification:")
print(f"  nums before: address={hex(addr_list_before)}")
print(f"  nums after : address={hex(addr_list_after)} (Address UNCHANGED! Modified in-place)")


# ==============================================================================
# SECTION 5: CPython Caching: Small Ints & String Interning
# ==============================================================================
print("\n--- 5. CPython Caching Optimizations ---")
"""
To save memory and execution speed, CPython pre-allocates and caches certain immutable objects:

1. Small Integer Cache:
   Integers between -5 and 256 (inclusive) are pre-allocated at Python startup.
   Any assignment in this range reuses the pre-existing singleton!

2. String Interning:
   Certain strings (like identifiers, short ASCII literals) are interned in a global dictionary.
"""

# Small integer cache test:
int_a = 100
int_b = 100
print(f"Small int 100: int_a is int_b? -> {int_a is int_b} (Same pre-allocated singleton)")

# Beyond small integer cache:
# (Note: Interactive REPL or separate lines prevent compiler-level constant folding)
large_a = int("1000")
large_b = int("1000")
print(f"Large int 1000: large_a is large_b? -> {large_a is large_b} (Separate heap objects!)")
print(f"  large_a addr: {hex(id(large_a))}")
print(f"  large_b addr: {hex(id(large_b))}")

# String interning test:
str1 = sys.intern("very_unique_custom_identifier_string")
str2 = sys.intern("very_unique_custom_identifier_string")
print(f"Interned strings: str1 is str2? -> {str1 is str2} (Addresses matched via sys.intern)")


# ==============================================================================
# SECTION 6: Classic Gotcha - Default Mutable Argument
# ==============================================================================
print("\n--- 6. Classic Gotcha: Default Mutable Argument ---")
"""
In Python, default parameter values are evaluated ONCE when the function is DEFINED,
NOT each time the function is called! If the default value is mutable, all calls
share the exact same object in memory.
"""


def buggy_append(item, target_list=[]):
    target_list.append(item)
    return target_list


print("Calling buggy_append('A'):", buggy_append("A"))
print("Calling buggy_append('B'):", buggy_append("B"))  # Unexpectedly retains 'A'!


def safe_append(item, target_list=None):
    if target_list is None:
        target_list = []  # Fresh list allocated on each invocation
    target_list.append(item)
    return target_list


print("Calling safe_append('A'):", safe_append("A"))
print("Calling safe_append('B'):", safe_append("B"))  # Clean and isolated!


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 2")
print("=" * 70)
print("1. Variables are references/labels pointing to objects on the heap, not storage boxes.")
print("2. 'is' checks pointer identity (id(a) == id(b)); '==' checks value equality.")
print("3. Aliasing happens when two variables reference the same mutable object.")
print("4. CPython pre-caches integers -5 to 256 and interns select strings.")
print("5. Never use mutable defaults in function signatures; use None + dynamic allocation.")
print("=" * 70)
