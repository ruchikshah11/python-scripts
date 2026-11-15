"""
================================================================================
Topic 6: Python Memory Allocation (pymalloc, Arenas, and Process RSS)
================================================================================

SYNOPSIS:
    Explores how CPython allocates and releases memory under the hood. Covers
    `sys.getsizeof()` limitations, object memory footprints, the pymalloc
    small-object allocator architecture (Arenas, Pools, Blocks), memory fragmentation,
    and why deleting large objects does not immediately reduce process Resident Set
    Size (RSS) memory back to the Operating System.

CONCEPTS COVERED:
    1. Object Sizing using sys.getsizeof(): Direct size vs deep container size.
    2. CPython's pymalloc Allocator Architecture:
       - Arenas (256 KB memory chunks requested from OS via mmap/malloc)
       - Pools (4 KB subdivisions within an Arena, dedicated to a specific block size)
       - Blocks (fixed-size slots: 8, 16, 24, ... up to 512 bytes)
    3. Small vs Large Object Allocation:
       - <= 512 bytes: Handled by pymalloc (no OS system call overhead).
       - > 512 bytes: Diverted directly to standard C library malloc().
    4. Memory Release Mechanics:
       - Why Python holds onto freed memory for future allocations.
       - Arenas can only be released to the OS if EVERY pool within the arena is empty!
    5. Fragmentation: Why memory cannot easily be returned to the OS.
    6. Practical Experiment: Monitoring process memory before and after deleting objects.

EXPECTED OUTPUT HIGHLIGHTS:
    - Accurate calculation of recursive container size.
    - Demonstrating that deleting 500,000 integers does not instantly shrink process RSS.
================================================================================
"""

import os
import sys
import resource

print("=" * 70)
print("TOPIC 6: Python Memory Allocation (pymalloc & Process RSS)")
print("=" * 70)


# ==============================================================================
# SECTION 1: sys.getsizeof() and Container Shallow Sizing
# ==============================================================================
print("\n--- 1. Accurate Sizing: sys.getsizeof() vs Deep Size ---")
"""
CRITICAL ACCURACY REQUIREMENT:
`sys.getsizeof()` only returns the direct memory consumed by the container struct itself!
It DOES NOT count the objects referenced inside the container!
"""

empty_list = []
nested_list = [1, 2, [3, 4], "hello"]

print(f"Empty list size     : {sys.getsizeof(empty_list)} bytes")
print(f"Nested list size    : {sys.getsizeof(nested_list)} bytes")
print("Notice: sys.getsizeof(nested_list) only counts the pointers in the array!")


def total_deep_size(obj, seen=None) -> int:
    """Recursively calculates the true total memory footprint of an object graph."""
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


print(f"Deep size of nested_list: {total_deep_size(nested_list)} bytes (includes sub-lists & strings)")


# ==============================================================================
# SECTION 2: CPython's pymalloc Architecture Explained
# ==============================================================================
print("\n--- 2. pymalloc Architecture (Arenas, Pools, Blocks) ---")
"""
CPython applications create and destroy millions of tiny short-lived objects.
Standard system `malloc()` causes high context-switch overhead and memory fragmentation.

To solve this, CPython implements 'pymalloc':
1. ARENA (256 KB):
   A continuous 256 KB memory chunk allocated from the OS virtual memory.
2. POOL (4 KB):
   An arena is divided into sixty-four 4 KB pools (matching OS memory page size).
   Each pool is dedicated to a SINGLE size-class of blocks (e.g., 16-byte pool, 32-byte pool).
3. BLOCK (8 to 512 bytes):
   A pool is carved into uniform blocks. When you create an object <= 512 bytes,
   pymalloc returns a free block in constant O(1) time.
"""
print("  * Arenas : 256 KB chunks from OS.")
print("  * Pools  : 4 KB page subdivisions, each assigned a specific size-class.")
print("  * Blocks : Fixed-size slots (8, 16, 24, ..., 512 bytes).")
print("  * Large objects (> 512 bytes) bypass pymalloc and go directly to C malloc.")


# ==============================================================================
# SECTION 3: Why Deleting Objects Does Not Return OS Memory Immediately
# ==============================================================================
print("\n--- 3. Why Process RSS Does Not Shrink After 'del' ---")
"""
COMMON MISCONCEPTION:
"If I delete a 200 MB list with 'del my_list' and call 'gc.collect()', my operating
system process memory (Task Manager / top) will immediately drop by 200 MB."
--> FALSE!

WHY?
1. The memory is returned to Python's private heap (pymalloc pools), NOT the OS!
   Python retains this memory so that future allocations can be satisfied instantly
   without expensive OS kernel system calls.
2. An Arena (256 KB) can ONLY be released back to the OS if EVERY SINGLE BLOCK
   across all 64 pools in that arena becomes completely vacant!
   If even ONE 16-byte object remains in the arena, the entire 256 KB page must stay mapped.
"""


def get_process_rss_mb() -> float:
    """Returns current process Resident Set Size (RSS) in MegaBytes using Linux /proc or resource."""
    try:
        # On Linux, /proc/self/statm column 1 gives total pages, column 2 gives resident pages
        with open("/proc/self/statm", "r") as f:
            resident_pages = int(f.read().split()[1])
            page_size_kb = os.sysconf("SC_PAGE_SIZE") / 1024
            return (resident_pages * page_size_kb) / 1024
    except Exception:
        # Fallback to resource module (ru_maxrss is peak in KB on Linux)
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


print(f"Initial Process Memory (RSS): {get_process_rss_mb():.2f} MB")

# Allocate 500,000 objects:
print("Allocating 500,000 integers in a list...")
large_dataset = [i * 100 for i in range(500_000)]
print(f"Memory after allocation      : {get_process_rss_mb():.2f} MB")

# Delete the reference:
print("Executing 'del large_dataset'...")
del large_dataset

import gc
gc.collect()

print(f"Memory after 'del' + gc      : {get_process_rss_mb():.2f} MB")
print("Notice: Memory does NOT drop back to baseline!")
print("The memory is cached in Python's allocator freelists ready for reuse.")


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 6")
print("=" * 70)
print("1. sys.getsizeof() is shallow; use recursive walkers for container sizing.")
print("2. pymalloc manages small objects (<= 512 bytes) inside Arenas -> Pools -> Blocks.")
print("3. Objects > 512 bytes are managed directly by OS malloc.")
print("4. Python maintains a private memory pool. Memory is rarely returned to the OS")
print("   until the entire 256 KB arena is completely free.")
print("=" * 70)
