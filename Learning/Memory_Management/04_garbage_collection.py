"""
================================================================================
Topic 4: Cyclic Garbage Collection & The `gc` Module
================================================================================

SYNOPSIS:
    Explains CPython's secondary memory management system: The Cyclic Garbage
    Collector. Demonstrates reference cycles (why reference counting fails to
    collect them), how the cyclic GC isolates reference islands, the 3 generations
    (Gen 0, Gen 1, Gen 2), collection thresholds, and programmatic control
    using the standard library `gc` module.

CONCEPTS COVERED:
    1. Reference Counting vs Garbage Collection.
    2. The Circular Reference Problem (Isolated Reference Islands).
    3. How Cyclic GC Works: Finding Reachable vs Unreachable Objects.
    4. Generational Garbage Collection:
       - Generation 0: Young, short-lived objects.
       - Generation 1: Intermediate survivors.
       - Generation 2: Long-lived objects.
       - The Weak Generational Hypothesis: Most objects die young.
    5. The `gc` Module API:
       - gc.collect(), gc.get_threshold(), gc.set_threshold()
       - gc.get_count(), gc.disable(), gc.enable()
    6. Practical Experiment: Creating an isolated reference cycle and collecting it.

EXPECTED OUTPUT HIGHLIGHTS:
    - Demonstrating that 'del' on a cyclic structure fails to deallocate immediately.
    - Explicit collection of the cycle with gc.collect().
    - Threshold inspection and generation counters.
================================================================================
"""

import gc
import sys

print("=" * 70)
print("TOPIC 4: Cyclic Garbage Collection & The gc Module")
print("=" * 70)


# ==============================================================================
# SECTION 1: Why Reference Counting Alone is Insufficient
# ==============================================================================
print("\n--- 1. The Circular Reference Problem ---")
"""
Reference counting has one fatal flaw: CIRCULAR REFERENCES.
If Object A points to Object B, and Object B points to Object A:
  - Both have a reference count of at least 1.
  - If we delete the external variables pointing to A and B, the two objects
    are now completely unreachable by our program!
  - Yet their reference counts will NEVER reach 0 because they point to each other!
Without a cyclic garbage collector, this memory would leak permanently!
"""


class Node:
    def __init__(self, name: str):
        self.name = name
        self.partner = None
        print(f"  [ALLOCATED Node] {self.name} at {hex(id(self))}")

    def __del__(self):
        print(f"  [COLLECTED Node] {self.name} at {hex(id(self))}")


def create_unreachable_cycle():
    print("\n  Inside create_unreachable_cycle():")
    node_a = Node("NodeA")
    node_b = Node("NodeB")

    # Create the cycle:
    node_a.partner = node_b
    node_b.partner = node_a

    print("  Cycle established (node_a <---> node_b).")
    print(f"  node_a refcount: {sys.getrefcount(node_a) - 1}")
    print(f"  node_b refcount: {sys.getrefcount(node_b) - 1}")
    print("  Exiting create_unreachable_cycle() scope...")


# Temporarily disable automatic cyclic GC so we can see the cycle persist!
gc.disable()
print("\nAutomatic GC is now DISABLED to observe reference leak:")
create_unreachable_cycle()

print("\nNotice: The function returned, but NodeA and NodeB were NOT deallocated!")
print("They are trapped in an unreachable circular reference island.")


# ==============================================================================
# SECTION 2: How Cyclic GC Resolves Reference Cycles
# ==============================================================================
print("\n--- 2. Collecting the Cycle with gc.collect() ---")
"""
How CPython's Cyclic GC algorithm works:
1. It maintains doubly-linked lists of all container objects (tracked objects).
2. It makes a trial copy of each object's reference count (`gc_refs`).
3. For each container, it traverses all objects it references and decrements their `gc_refs`.
4. After traversing all internal references:
   - If an object's `gc_refs` is > 0, it means it is referenced from OUTSIDE the cycle
     (it is REACHABLE). It and everything it references are preserved.
   - If an object's `gc_refs` drops to 0, it was ONLY referenced internally by the cycle!
     (it is UNREACHABLE). The GC marks it for destruction!
"""

print("Triggering manual collection with gc.collect():")
unreachable_count = gc.collect()
print(f"gc.collect() successfully reclaimed {unreachable_count} unreachable objects!")

# Re-enable automatic GC
gc.enable()
print("Automatic GC re-enabled.")


# ==============================================================================
# SECTION 3: Generational Garbage Collection (Gen 0, 1, 2)
# ==============================================================================
print("\n--- 3. Generational Garbage Collection ---")
"""
Scanning all objects in memory on every cycle would be far too slow.
To optimize this, CPython uses GENERATIONAL GC based on the:
**Weak Generational Hypothesis**: "Most objects die young."

CPython divides tracked container objects into 3 Generations:
- Generation 0: Newly allocated container objects. Scanned frequently.
- Generation 1: Objects that survive a Gen 0 collection. Scanned less frequently.
- Generation 2: Objects that survive a Gen 1 collection (long-lived / permanent). Scanned rarely.
"""

# Inspect current collection thresholds:
# Defaults are typically (700, 10, 10)
thresholds = gc.get_threshold()
print(f"GC Thresholds (Gen0, Gen1, Gen2): {thresholds}")
"""
Explanation of (700, 10, 10):
- Gen 0 runs when (allocations - deallocations) exceeds 700.
- Gen 1 runs once every 10 Gen 0 collections.
- Gen 2 runs once every 10 Gen 1 collections (full sweep).
"""

# Inspect current allocation counters:
counts = gc.get_count()
print(f"Current GC Counts (Gen0, Gen1, Gen2): {counts}")


# ==============================================================================
# SECTION 4: Inspecting and Tracking Containers
# ==============================================================================
print("\n--- 4. What Objects Are Tracked by Cyclic GC? ---")
"""
IMPORTANT PERFORMANCE NOTE:
CPython's Cyclic GC ONLY tracks containers that can potentially hold references
to other objects!
- Tracked: dict, list, tuple (if containing mutable items), set, custom classes, functions.
- NOT Tracked: atomic types like int, float, str, bytes, tuple of only ints/strings.
  (Atomic types can never form a circular reference, so the GC ignores them!)
"""

atomic_int = 42
atomic_str = "hello"
container_list = [1, 2, 3]

print(f"Is integer 42 tracked by GC?       : {gc.is_tracked(atomic_int)}")
print(f"Is string tracked by GC?          : {gc.is_tracked(atomic_str)}")
print(f"Is list container tracked by GC?  : {gc.is_tracked(container_list)}")


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 4")
print("=" * 70)
print("1. Reference counting handles 99% of memory cleanup instantly and deterministically.")
print("2. The Cyclic GC exists solely to detect and break isolated circular references.")
print("3. Generational GC organizes objects into 3 generations based on age.")
print("4. Atomic objects (int, str) are never tracked by the cyclic GC to maximize speed.")
print("5. Use gc.collect() in batch jobs or long-running daemons after releasing large cyclic graphs.")
print("=" * 70)
