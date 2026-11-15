"""
================================================================================
Topic 3: Garbage Collection & Circular References
================================================================================

RELATABLE ANALOGY:
    Think of a 2-person island:
    - Alice holds Bob's hand, and Bob holds Alice's hand (a reference loop).
    - If the bridge connecting the island to the mainland collapses (all outside
      variables are deleted), Alice and Bob can only reach each other.
    - Reference counting cannot save this: both people still have 1 hand held!
    - The Cyclic Garbage Collector is the rescue boat that surveys the whole island,
      sees that NO ONE from the mainland is holding them, and cleans up the island!

CONCEPTS COVERED:
    1. Reference Counting vs Garbage Collection.
    2. Why Circular References Cause Memory Leaks in pure reference counters.
    3. How CPython's Cyclic GC Detects and Destroys Cycles (Trial Decrement).
    4. Generational Garbage Collection:
       - Generation 0: Young objects (frequently scanned).
       - Generation 1: Intermediate survivors.
       - Generation 2: Long-lived objects (rarely scanned).
       - The Weak Generational Hypothesis: Most objects die young.
    5. The `gc` Module API: `gc.collect()`, `gc.get_threshold()`, `gc.disable()`.

PYTHON SPEC VS CPYTHON IMPLEMENTATION:
    - Python Specification: Does not define how or when cycles are broken.
    - CPython Detail: Uses a 3-generation cyclic garbage collector running in the background.
================================================================================
"""

import gc
import sys

print("=" * 70)
print("TOPIC 3: Garbage Collection & Circular References")
print("=" * 70)


# ==============================================================================
# SECTION 1: The Circular Reference Problem
# ==============================================================================
print("\n--- 1. Why Reference Counting Alone Fails: Circular References ---")
"""
If Object A references Object B, and Object B references Object A:
  - Both have a reference count of at least 1.
  - If we delete the external variables pointing to them, they become
    completely UNREACHABLE by the program.
  - Yet their reference counts never hit 0 because they reference each other!
"""


class CyclicNode:
    def __init__(self, name: str):
        self.name = name
        self.partner = None
        print(f"  [ALLOCATED] Node '{self.name}' at {hex(id(self))}")

    def __del__(self):
        print(f"  [COLLECTED] Node '{self.name}' at {hex(id(self))}")


def create_isolated_cycle():
    print("  Creating Node1 and Node2 inside function...")
    node1 = CyclicNode("Alpha")
    node2 = CyclicNode("Beta")

    # Connect in a circular loop:
    node1.partner = node2
    node2.partner = node1

    print("  Cycle established: node1.partner -> node2, and node2.partner -> node1")
    print("  Exiting function... local names 'node1' and 'node2' are destroyed.")


# Temporarily disable automatic cyclic GC to demonstrate the memory leak
gc.disable()
print("\nStep A: Automatic GC is DISABLED to observe the leak:")
create_isolated_cycle()

print("\nNotice: The function finished, but Alpha and Beta were NOT deallocated!")
print("Their reference counts are still 1 because they point to each other.")


# ==============================================================================
# SECTION 2: How the Cyclic GC Fixes the Leak (`gc.collect()`)
# ==============================================================================
print("\n--- 2. How the Cyclic GC Reclaims Cycles ---")
"""
How CPython's Cyclic GC works:
1. It tracks all container objects (lists, dicts, custom classes).
2. It makes a trial copy of each object's reference count (`gc_refs`).
3. For each container, it decrements the `gc_refs` of the objects it points to.
4. After traversing internal links:
   - If `gc_refs == 0`: The object was ONLY referenced from inside the cycle!
     It is unreachable from the outside world and is safe to destroy.
   - If `gc_refs > 0`: The object has an active external reference.
"""

print("Step B: Manually running `gc.collect()` to break the cycle:")
unreachable_count = gc.collect()
print(f"gc.collect() successfully identified and collected {unreachable_count} unreachable objects!")

# Re-enable automatic GC
gc.enable()
print("Automatic GC re-enabled.")


# ==============================================================================
# SECTION 3: Generational Garbage Collection
# ==============================================================================
print("\n--- 3. Generational Garbage Collection (Gen 0, 1, 2) ---")
"""
Scanning all objects in RAM constantly would destroy performance.
CPython optimizes this using the WEAK GENERATIONAL HYPOTHESIS:
"Most objects die very shortly after creation."

CPython divides tracked containers into 3 generations:
- Generation 0: Brand new container objects. Checked very frequently.
- Generation 1: Survived one Gen 0 collection. Checked less frequently.
- Generation 2: Survived multiple collections (long-lived / permanent). Checked rarely.
"""

# Inspect current collection thresholds:
thresholds = gc.get_threshold()
print(f"GC Thresholds (Gen0, Gen1, Gen2): {thresholds}")
"""
Default is typically (700, 10, 10):
- Gen 0 runs when (allocations - deallocations) > 700.
- Gen 1 runs once every 10 Gen 0 collections.
- Gen 2 runs once every 10 Gen 1 collections (full sweep).
"""

# Inspect current generation counters:
counts = gc.get_count()
print(f"Current Generation Counts: {counts}")


# ==============================================================================
# SECTION 4: What Objects Are Tracked by Cyclic GC?
# ==============================================================================
print("\n--- 4. GC Tracked vs Untracked Objects ---")
"""
IMPORTANT PERFORMANCE FACT:
CPython's Cyclic GC only tracks objects that can HOLD references to other objects!
Atomic types like integers, floats, strings, and tuples of only ints/strings
cannot form cycles. To stay fast, the GC never tracks them!
"""

atomic_val = 12345
atomic_str = "hello"
container_obj = [1, 2, 3]

print(f"Is integer tracked by GC?  : {gc.is_tracked(atomic_val)}")
print(f"Is string tracked by GC?   : {gc.is_tracked(atomic_str)}")
print(f"Is list tracked by GC?     : {gc.is_tracked(container_obj)}")


# ==============================================================================
# INTERVIEW QUESTIONS FOR TOPIC 3
# ==============================================================================
print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS - Topic 3")
print("=" * 70)
print("Q1: If Python has reference counting, why does it need a garbage collector?")
print("A1: Because reference counting cannot detect circular references. When two or")
print("    more unreachable objects point to each other, their counts never hit zero.")
print("\nQ2: What is the Weak Generational Hypothesis?")
print("A2: The observation that in most programs, the vast majority of objects are short-lived.")
print("    Focusing GC cycles on young objects (Gen 0) minimizes CPU pause times.")
print("=" * 70)
