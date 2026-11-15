"""
================================================================================
Topic 5: Memory Optimization & Profiling
================================================================================

RELATABLE ANALOGY:
    Think of storage optimization:
    - Lists are like pre-ordering 1,000,000 books and stacking them in your living room.
    - Generators are like a library card: you check out only the 1 book you are
      reading right now, then return it before getting the next!
    - `__slots__` is like custom form-fitting packaging instead of a giant cardboard
      box with bubble wrap for every single item.

CONCEPTS COVERED:
    1. Memory Sizing with `sys.getsizeof()` (Direct container vs deep object tree).
    2. Lazy Evaluation: Generators vs Eager Lists (O(1) vs O(N) memory).
    3. Eliminating Class Instance Overhead with `__slots__`:
       - Standard Python classes use `__dict__` (~100-150 bytes per instance).
       - `__slots__` stores attributes in a fixed-size C pointer array.
       - Saves 60-70% RAM across large collections of objects!
    4. Memory Profiling with the standard library `tracemalloc` module:
       - Starting trace, taking snapshots, comparing diffs, identifying memory hogs.

EXPECTED OUTPUT HIGHLIGHTS:
    - 40,000x memory reduction using generators over lists.
    - 65%+ memory reduction across 100,000 instances using `__slots__`.
    - Line-by-line memory allocation tracking with `tracemalloc`.
================================================================================
"""

import sys
import gc
import tracemalloc

print("=" * 70)
print("TOPIC 5: Memory Optimization & Profiling")
print("=" * 70)


# ==============================================================================
# SECTION 1: Object Sizing with sys.getsizeof()
# ==============================================================================
print("\n--- 1. Object Sizing with sys.getsizeof() ---")
"""
IMPORTANT NOTE:
`sys.getsizeof()` returns only the DIRECT memory allocated for the object struct itself.
For containers (like lists or dicts), it measures the array of POINTERS, NOT the
underlying objects being pointed to!
"""

empty_list = []
filled_list = [1, 2, [3, 4], "hello"]

print(f"Empty list size       : {sys.getsizeof(empty_list)} bytes")
print(f"Filled list shallow   : {sys.getsizeof(filled_list)} bytes (only counts 4 pointers!)")


def total_deep_size(obj, seen=None) -> int:
    """Recursively walks an object tree to compute total deep memory usage."""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum(total_deep_size(k, seen) + total_deep_size(v, seen) for k, v in obj.items())
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(total_deep_size(item, seen) for item in obj)
    if hasattr(obj, "__dict__"):
        size += total_deep_size(obj.__dict__, seen)

    return size


print(f"Filled list true deep : {total_deep_size(filled_list)} bytes (includes sub-lists & strings)")


# ==============================================================================
# SECTION 2: Generators vs Lists (Lazy Evaluation)
# ==============================================================================
print("\n--- 2. Lazy Evaluation: Generators vs Lists ---")

n_elements = 1_000_000

# Eager List: Allocates 1,000,000 pointers in RAM upfront
list_data = [i for i in range(n_elements)]

# Lazy Generator: Computes values on demand (O(1) memory)
gen_data = (i for i in range(n_elements))

list_mem = sys.getsizeof(list_data)
gen_mem = sys.getsizeof(gen_data)

print(f"Elements: {n_elements:,}")
print(f"List comprehension memory : {list_mem:,} bytes ({list_mem / (1024 * 1024):.2f} MB)")
print(f"Generator expression memory: {gen_mem:,} bytes ({gen_mem / 1024:.2f} KB)")
print(f"Memory reduction ratio   : {list_mem / gen_mem:,.1f}x less memory!")

del list_data  # Free memory


# ==============================================================================
# SECTION 3: Class Memory Optimization with __slots__
# ==============================================================================
print("\n--- 3. Class Optimization with __slots__ ---")
"""
By default, Python creates a dynamic dictionary (`self.__dict__`) for every instance
to allow arbitrary attribute additions at runtime.
If you instantiate 100,000 objects, 100,000 dictionaries waste massive RAM.

`__slots__ = ('x', 'y')` replaces `__dict__` with a compact fixed C array of pointers!
"""


class StandardPoint:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class SlottedPoint:
    __slots__ = ("x", "y")  # Suppresses __dict__ allocation

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


p_std = StandardPoint(1.0, 2.0)
p_slot = SlottedPoint(1.0, 2.0)

print(f"StandardPoint has __dict__? : {'__dict__' in dir(p_std)}")
print(f"SlottedPoint has __dict__?  : {'__dict__' in dir(p_slot)}")

# Benchmark across 100,000 instances using tracemalloc:
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
std_instances = [StandardPoint(float(i), float(i)) for i in range(100_000)]
snap2 = tracemalloc.take_snapshot()

del std_instances
gc.collect()

snap3 = tracemalloc.take_snapshot()
slotted_instances = [SlottedPoint(float(i), float(i)) for i in range(100_000)]
snap4 = tracemalloc.take_snapshot()

del slotted_instances
gc.collect()
tracemalloc.stop()

std_mem_kb = sum(s.size for s in snap2.compare_to(snap1, "lineno")) / 1024
slot_mem_kb = sum(s.size for s in snap4.compare_to(snap3, "lineno")) / 1024

print(f"Memory for 100,000 Standard instances: {std_mem_kb:,.1f} KB")
print(f"Memory for 100,000 Slotted instances : {slot_mem_kb:,.1f} KB")
print(f"Memory savings with __slots__        : {(1 - slot_mem_kb / std_mem_kb) * 100:.1f}% less RAM!")


# ==============================================================================
# SECTION 4: Memory Profiling with tracemalloc
# ==============================================================================
print("\n--- 4. Memory Profiling with tracemalloc ---")
"""
The built-in `tracemalloc` module tracks memory allocations directly to the
Python source code file and line number where they occurred!
"""

tracemalloc.start()


def data_pipeline():
    # Allocates strings and dictionary
    raw_lines = [f"Data_Row_{i}" for i in range(50_000)]
    index_map = {k: k * 3 for k in range(25_000)}
    return raw_lines, index_map


output = data_pipeline()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 3 memory allocation lines in pipeline:")
for stat in top_stats[:3]:
    print(f"  {stat}")

tracemalloc.stop()


# ==============================================================================
# INTERVIEW QUESTIONS FOR TOPIC 5
# ==============================================================================
print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS - Topic 5")
print("=" * 70)
print("Q1: What are the trade-offs of using `__slots__`?")
print("A1: Pros: Substantial memory savings (60-70%) and slightly faster attribute access.")
print("    Cons: Cannot dynamically add new attributes at runtime; multiple inheritance")
print("    with multiple slotted base classes can cause instance layout conflicts.")
print("\nQ2: How does `tracemalloc` help identify memory leaks in production?")
print("A2: It hooks directly into Python memory allocation calls and correlates them with")
print("    exact file and line numbers, allowing snapshot comparison (diffs) over time.")
print("=" * 70)
