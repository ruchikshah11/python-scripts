"""
================================================================================
Topic 7: Memory Optimization & Profiling in Python
================================================================================

SYNOPSIS:
    Master practical memory optimization techniques in Python. Explores
    `__slots__` for eliminating per-instance `__dict__` overhead, generator
    streaming vs eager lists, efficient built-in data structures (array, deque),
    weak references (`weakref`), avoiding unnecessary object churn, and memory
    profiling using the standard library `tracemalloc` module.

CONCEPTS COVERED:
    1. Reducing Class Instance Overhead with `__slots__`:
       - How standard Python objects use dynamic `__dict__` (~100-150 bytes overhead).
       - How `__slots__` replaces `__dict__` with a fixed-size C array of pointers.
       - Memory reduction benchmarking (often 60%-70% RAM reduction!).
    2. Lazy Evaluation: Generators vs Eager Lists.
    3. Memory-Efficient Data Structures:
       - `array.array` vs Python lists for homogeneous numeric data.
       - `collections.deque` vs lists for FIFO queues.
    4. Weak References with `weakref`: Caching without preventing garbage collection.
    5. Memory Profiling with `tracemalloc`:
       - Starting trace, taking snapshots, comparing diffs, identifying top memory hogs.

EXPECTED OUTPUT HIGHLIGHTS:
    - Side-by-side memory comparison of 100,000 standard vs `__slots__` objects.
    - Generational memory savings with `tracemalloc`.
    - Demonstration of automatic weakref cleanup upon object destruction.
================================================================================
"""

import sys
import array
import weakref
import tracemalloc

print("=" * 70)
print("TOPIC 7: Memory Optimization & Profiling (slots & tracemalloc)")
print("=" * 70)


# ==============================================================================
# SECTION 1: Optimizing Class Instances with __slots__
# ==============================================================================
print("\n--- 1. Class Memory Optimization with __slots__ ---")
"""
By default, every custom Python object stores its attributes inside a private
dictionary (`self.__dict__`). A dictionary has high memory overhead to support
dynamic key additions.

If you create 1,000,000 instances of a class (e.g. data records, points, nodes),
allocating 1,000,000 dictionaries wastes hundreds of megabytes of RAM!

Solution: Define `__slots__ = ('attr1', 'attr2')`.
- Suppresses the creation of `__dict__`.
- Attributes are stored in a compact fixed-size C array of pointer descriptors.
- Saves 60-70% memory per instance!
"""


class StandardPoint:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class SlottedPoint:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


p_std = StandardPoint(1.0, 2.0, 3.0)
p_slot = SlottedPoint(1.0, 2.0, 3.0)

print(f"StandardPoint has __dict__? : {'__dict__' in dir(p_std)}")
print(f"SlottedPoint has __dict__?  : {'__dict__' in dir(p_slot)}")

# Benchmark memory across 100,000 instances using tracemalloc:
tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
std_instances = [StandardPoint(float(i), float(i), float(i)) for i in range(100_000)]
snap2 = tracemalloc.take_snapshot()

del std_instances
import gc
gc.collect()

snap3 = tracemalloc.take_snapshot()
slotted_instances = [SlottedPoint(float(i), float(i), float(i)) for i in range(100_000)]
snap4 = tracemalloc.take_snapshot()

del slotted_instances
gc.collect()
tracemalloc.stop()

# Compute memory differences:
std_mem_kb = sum(stat.size for stat in snap2.compare_to(snap1, "lineno")) / 1024
slot_mem_kb = sum(stat.size for stat in snap4.compare_to(snap3, "lineno")) / 1024

print(f"Memory for 100,000 Standard instances: {std_mem_kb:,.1f} KB")
print(f"Memory for 100,000 Slotted instances : {slot_mem_kb:,.1f} KB")
print(f"Memory savings with __slots__        : {(1 - slot_mem_kb / std_mem_kb) * 100:.1f}% less RAM!")


# ==============================================================================
# SECTION 2: Efficient Data Structures: array.array vs list
# ==============================================================================
print("\n--- 2. Homogeneous Data: array.array vs list ---")
"""
A Python `list` stores POINTERS to individual PyObject integers on the heap.
Each integer is 28 bytes + 8-byte pointer = ~36 bytes per number!

`array.array('i')` stores raw C integers packed contiguously in memory:
Only 4 bytes per integer!
"""

n_items = 100_000
python_list = list(range(n_items))
c_array = array.array("i", range(n_items))

print(f"Size of list of {n_items:,} ints   : {sys.getsizeof(python_list):,} bytes (shallow pointers only)")
print(f"Size of array.array('i') contig : {sys.getsizeof(c_array):,} bytes (actual raw data payload)")
print(f"Array storage is {sys.getsizeof(python_list) / sys.getsizeof(c_array):.1f}x smaller!")


# ==============================================================================
# SECTION 3: Weak References with weakref
# ==============================================================================
print("\n--- 3. Weak References with weakref ---")
"""
A standard reference increases the object's `ob_refcnt`, preventing deallocation.
A `weakref` reference allows you to access an object WITHOUT increasing its refcount!
If all strong references are deleted, the object is destroyed immediately,
and the weak reference safely resolves to `None`.
Ideal for in-memory caches and circular parent-child relationships.
"""


class CacheableResource:
    def __init__(self, name: str):
        self.name = name


resource = CacheableResource("HeavyDataset")
weak_handle = weakref.ref(resource)

print(f"Strong reference exists? -> resource is {weak_handle()}")

# Delete the only strong reference:
del resource
print(f"After 'del resource', weak_handle() resolves to: {weak_handle()} (Safely GC'd without leaks!)")


# ==============================================================================
# SECTION 4: Memory Profiling with tracemalloc
# ==============================================================================
print("\n--- 4. Profiling Memory with tracemalloc ---")
"""
The standard library `tracemalloc` module tracks memory allocations back to
the exact Python source code filename and line number!
"""

tracemalloc.start()


def memory_hungry_task():
    data = [f"Record_{i}" for i in range(50_000)]
    mapping = {k: k * 2 for k in range(25_000)}
    return data, mapping


task_output = memory_hungry_task()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 3 memory allocation lines:")
for stat in top_stats[:3]:
    print(f"  {stat}")

tracemalloc.stop()


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 7")
print("=" * 70)
print("1. Use `__slots__` on classes with thousands of instances to strip `__dict__` overhead.")
print("2. Use `array.array` or numpy arrays for large numeric collections to avoid pointer boxing.")
print("3. Use `weakref` for caches and observer patterns to avoid accidental memory leaks.")
print("4. Use `tracemalloc` to pinpoint exact lines of code driving memory bloat in production.")
print("=" * 70)
