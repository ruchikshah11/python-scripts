"""
================================================================================
Topic 1: Memory Basics
================================================================================

RELATABLE ANALOGY:
    Think of Python memory like a warehouse:
    - The OBJECT is an item sitting on a shelf in the warehouse (the Heap).
    - The VARIABLE is a sticky note or barcode tag pointing to that shelf.
    - You don't store items inside the sticky notes; you stick the note on the item!

CONCEPTS COVERED:
    1. Variables as Named References (Sticky Notes, not Boxes).
    2. Everything is an Object in Memory (The PyObject Header).
    3. CPython Stack vs Heap:
       - Stack: Execution frames, local variable names, and object pointers.
       - Heap: Private memory area where ALL Python objects live.
    4. Object Identity: `id()`, pointer equality (`is`), and value equality (`==`).
    5. CPython Optimizations: Small Integer Caching (-5 to 256) and String Interning.

PYTHON SPEC VS CPYTHON IMPLEMENTATION:
    - Python Specification: All variables are references to objects.
    - CPython Detail: `id(obj)` returns the actual C memory address of the PyObject struct.
================================================================================
"""

import sys
import inspect

print("=" * 70)
print("TOPIC 1: Python Memory Basics")
print("=" * 70)


# ==============================================================================
# SECTION 1: Variables as References (Sticky Note Analogy)
# ==============================================================================
print("\n--- 1. Variables as References (Not Storage Boxes) ---")

# Step 1: Create a list object [10, 20, 30] on the heap
a = [10, 20, 30]

# Step 2: 'b = a' does NOT create a second list. It sticks a second label on the same object!
b = a

print(f"Variable 'a' points to address: {hex(id(a))} (value: {a})")
print(f"Variable 'b' points to address: {hex(id(b))} (value: {b})")
print(f"Do 'a' and 'b' reference the EXACT same object? -> {a is b}")

# Expected Output:
# Both print the exact same hex address and 'a is b' is True.


# ==============================================================================
# SECTION 2: Stack vs Heap in CPython
# ==============================================================================
print("\n--- 2. Stack vs Heap in CPython ---")
"""
COMMON MISCONCEPTION:
"In Python, primitive numbers go on the stack, while lists and objects go on the heap."
--> FALSE! In CPython, ALL objects (numbers, strings, lists, functions) live on the HEAP!

So what lives on the Stack?
1. Call Frames: Whenever a function is called, a frame is pushed onto the call stack.
2. Local Pointers: The frame holds local variable names and memory addresses (pointers).
   These pointers point to the actual objects resting on the heap.
"""


def demonstrate_stack_frame(depth: int):
    # 'local_number' is a variable name in this frame pointing to an integer on the heap
    local_number = 500 + depth
    current_frame = inspect.currentframe()

    print(f"  [Stack Frame Depth {depth}]")
    print(f"    Function Name    : {current_frame.f_code.co_name}")
    print(f"    Variable Pointer : 'local_number' -> Heap Address {hex(id(local_number))}")

    if depth < 2:
        demonstrate_stack_frame(depth + 1)


demonstrate_stack_frame(1)


# ==============================================================================
# SECTION 3: The PyObject Header (Why Python Objects Have Overhead)
# ==============================================================================
print("\n--- 3. Everything is an Object (PyObject Header) ---")
"""
In C, a 64-bit integer is just 8 raw bytes.
In Python, an integer is a complete C struct called `PyLongObject` with metadata:
- `ob_refcnt` (8 bytes): Reference counter.
- `ob_type`   (8 bytes): Pointer to type object (&PyLong_Type).
- `ob_size`   (8 bytes): Digit count for arbitrary precision.
- Digit payload: The actual number value.

This is why even a small integer in Python takes 28 bytes!
"""

sample_int = 42
sample_str = "Memory"
empty_list = []

print(f"Integer 42 size   : {sys.getsizeof(sample_int)} bytes (includes 24 bytes of PyObject overhead)")
print(f"String '{sample_str}' size : {sys.getsizeof(sample_str)} bytes")
print(f"Empty list [] size: {sys.getsizeof(empty_list)} bytes (container header)")


# ==============================================================================
# SECTION 4: Object Identity (`id()`, `is`, and `==`)
# ==============================================================================
print("\n--- 4. Object Identity: 'is' vs '==' ---")
"""
- id(x): In CPython, returns the exact memory address of object x.
- '==' : Checks VALUE EQUALITY (calls __eq__()). Do they contain the same data?
- 'is' : Checks IDENTITY (id(a) == id(b)). Are they the exact same object in memory?
"""

list1 = [1, 2, 3]
list2 = [1, 2, 3]

print(f"list1: {list1} at {hex(id(list1))}")
print(f"list2: {list2} at {hex(id(list2))}")
print(f"list1 == list2 : {list1 == list2} (Same content/value)")
print(f"list1 is list2 : {list1 is list2} (Different objects on heap)")


# ==============================================================================
# SECTION 5: CPython Optimizations: Small Integer Cache
# ==============================================================================
print("\n--- 5. CPython Small Integer Caching (-5 to 256) ---")
"""
To save memory and CPU time, CPython pre-allocates an array of all integers
from -5 to 256 at startup. Any reference to an integer in this range reuses
the existing singleton!
"""

num1 = 200
num2 = 200
print(f"num1=200, num2=200: num1 is num2? -> {num1 is num2} (Cached singleton!)")

# Numbers outside -5 to 256 are allocated as separate objects
big1 = int("1000")
big2 = int("1000")
print(f"big1=1000, big2=1000: big1 is big2? -> {big1 is big2} (Distinct heap allocations)")
print(f"  big1 address: {hex(id(big1))}")
print(f"  big2 address: {hex(id(big2))}")


# ==============================================================================
# SECTION 6: Practical Experiment & Common Misconceptions
# ==============================================================================
print("\n--- 6. Common Misconception: Reassignment vs Mutation ---")

# Reassignment (Immutable):
val = 10
addr_before = id(val)
val += 1  # Does NOT modify 10. Allocates a new integer 11 and repoints 'val'!
addr_after = id(val)
print("Reassigning immutable integer (val += 1):")
print(f"  Address changed? -> {addr_before != addr_after} (Old={hex(addr_before)}, New={hex(addr_after)})")

# In-Place Mutation (Mutable):
my_list = [1, 2]
list_addr_before = id(my_list)
my_list.append(3)  # Modifies the list IN-PLACE at the exact same address
list_addr_after = id(my_list)
print("Mutating mutable list (my_list.append(3)):")
print(f"  Address changed? -> {list_addr_before != list_addr_after} (Same address: {hex(list_addr_before)})")


# ==============================================================================
# INTERVIEW QUESTIONS FOR TOPIC 1
# ==============================================================================
print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS - Topic 1")
print("=" * 70)
print("Q1: What does `id(obj)` return in Python?")
print("A1: In CPython, it returns the actual memory address of the PyObject struct.")
print("    In the language spec, it is guaranteed only to be a unique integer for its lifetime.")
print("\nQ2: Where do Python objects live: stack or heap?")
print("A2: In CPython, ALL Python objects reside on the private heap. The call stack")
print("    stores execution frames containing variable names and reference pointers.")
print("=" * 70)
