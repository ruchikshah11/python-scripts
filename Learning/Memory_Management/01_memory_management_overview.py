"""
================================================================================
Topic 1: Python Memory Management Overview
================================================================================

SYNOPSIS:
    An in-depth introduction to how Python manages memory. Explains object
    creation, storage on the private heap, references, stack vs heap in CPython,
    the multi-layer memory allocation hierarchy, and Python's memory lifecycle.

CONCEPTS COVERED:
    1. Python Language Spec vs CPython Implementation Details.
    2. Everything is an Object: Headers, PyObject, Type Pointers, and Payloads.
    3. The Python Private Heap and Object Storage.
    4. CPython Call Stack vs Heap (Call frames, primitive pointers vs heap objects).
    5. Python's Multi-Tier Memory Allocator Architecture (PyObject vs Pymalloc vs OS).
    6. The Object Lifecycle: Allocation -> Referencing -> Deallocation.

EXPECTED OUTPUT HIGHLIGHTS:
    - Object addresses in hexadecimal and integer format.
    - Inspection of PyObject overhead via sys.getsizeof().
    - Demonstration of call stack frame inspection with inspect module.
================================================================================
"""

import sys
import inspect

print("=" * 70)
print("TOPIC 1: Python Memory Management Overview")
print("=" * 70)


# ==============================================================================
# SECTION 1: Language Specification vs CPython Implementation
# ==============================================================================
print("\n--- 1. Python Language vs CPython Implementation ---")
"""
CRITICAL CONCEPT:
Python is a language specification (syntax, semantics, data model).
CPython is the reference implementation written in C (the one you download from python.org).

- Automatic memory management is part of the language specification.
- Reference counting + cyclic generational GC is SPECIFIC to CPython!
  (Other implementations like PyPy use tracing GC; Jython uses JVM GC; IronPython uses CLR GC).
"""

print(f"Python Implementation : {sys.implementation.name}")
print(f"Python Version        : {sys.version.split()[0]}")
print(f"Pointer Size (bytes)  : {sys.maxsize.bit_length() // 8 + 1} bytes (64-bit architecture)")


# ==============================================================================
# SECTION 2: Everything is an Object (PyObject in CPython)
# ==============================================================================
print("\n--- 2. Everything is an Object & The PyObject Header ---")
"""
In CPython, EVERY entity (integers, strings, functions, modules, classes) is an object
allocated on Python's private heap as a C struct:

struct _object {
    _PyObject_HEAD_EXTRA    // Doubly-linked list pointers for tracing/debug
    Py_ssize_t ob_refcnt;   // 8 bytes: 64-bit reference counter
    PyTypeObject *ob_type;  // 8 bytes: pointer to type object (e.g., &PyLong_Type)
};

For variable-length objects (lists, tuples, strings), PyVarObject adds:
    Py_ssize_t ob_size;     // 8 bytes: number of items in sequence

Because of this overhead, even a simple integer in Python is NOT a raw 4-byte C integer!
"""

n = 42
s = "Hello, Memory!"
lst = [1, 2, 3]

print(f"Integer 42 size     : {sys.getsizeof(n)} bytes (includes refcount + type pointer + digit payload)")
print(f"String '{s}' size   : {sys.getsizeof(s)} bytes")
print(f"Empty list [] size  : {sys.getsizeof([])} bytes (just the empty list container struct)")
print(f"List [1, 2, 3] size : {sys.getsizeof(lst)} bytes (container struct + 3 pointer slots)")


# ==============================================================================
# SECTION 3: Stack vs Heap in CPython
# ==============================================================================
print("\n--- 3. Stack vs Heap in CPython ---")
"""
COMMON MISCONCEPTION:
"In Python, primitive integers go on the stack, while objects go on the heap."
--> FALSE! In CPython, ALL Python objects live on the private heap.

So what is on the Stack?
1. C Call Stack: C functions executing within the CPython binary.
2. Python Call Stack: PyFrameObject structures representing active function call frames.
   - The frame stores local variable NAMES and POINTERS (references) to objects.
   - The actual OBJECTS being pointed to ALWAYS reside on the heap!
"""


def demonstrate_call_stack(level: int):
    # local_var is a reference residing in the current frame's fastlocals array
    local_val = 1000 + level
    current_frame = inspect.currentframe()

    print(f"  [Frame Level {level}]")
    print(f"    Function Name    : {current_frame.f_code.co_name}")
    print(f"    Local pointer to : val={local_val} (heap addr={hex(id(local_val))})")

    if level < 2:
        demonstrate_call_stack(level + 1)


demonstrate_call_stack(1)


# ==============================================================================
# SECTION 4: Python's Multi-Tier Memory Allocator Architecture
# ==============================================================================
print("\n--- 4. Python's Memory Allocator Hierarchy ---")
"""
To avoid high overhead from repeated OS system calls (malloc/free/brk/mmap),
CPython employs a 4-layer memory hierarchy:

Layer +3 (User level)          : High-level Python code (lists, dicts, objects)
Layer +2 (Object-specific)     : Type allocators (e.g. integer freelists, PyList_New)
Layer +1 (Python Core / Heap)  : 'pymalloc' (specialized small object allocator for <= 512 bytes)
                                 Organized into Arenas (256 KB) -> Pools (4 KB) -> Blocks (8-512 bytes)
Layer  0 (System / OS)         : OS Virtual Memory Allocator (malloc, free, VirtualAlloc, mmap)
"""
print("  Layer +3: Python application code creating objects")
print("  Layer +2: Object-specific allocators & freelists")
print("  Layer +1: 'pymalloc' small-object allocator (<= 512 bytes; arenas, pools, blocks)")
print("  Layer  0: OS C-runtime malloc / system virtual memory manager")


# ==============================================================================
# SECTION 5: The Object Lifecycle
# ==============================================================================
print("\n--- 5. The Complete Object Lifecycle ---")
"""
1. ALLOCATION: Memory requested from pymalloc or system malloc; PyObject header initialized.
2. INITIALIZATION: __new__ allocates memory; __init__ populates attributes.
3. REFERENCING & USAGE: Variables bind to object address; refcount increases/decreases.
4. DEALLOCATION: Refcount drops to 0; tp_dealloc method frees memory or returns to freelist.
"""


class LifecycleTracker:
    def __init__(self, name: str):
        self.name = name
        print(f"  --> [1. CREATED] {self.name} at {hex(id(self))}")

    def __del__(self):
        # NOTE: __del__ is called right before CPython deallocates the object
        print(f"  <-- [4. DEALLOCATED] {self.name} at {hex(id(self))}")


print("Creating and destroying an object within a temporary scope:")


def temporary_scope():
    obj = LifecycleTracker("TemporaryWorker")
    print(f"      Inside scope: {obj.name} is active")
    # When temporary_scope exits, obj goes out of scope -> refcount drops to 0 -> __del__ triggers


temporary_scope()
print("After temporary scope exited, object was deallocated automatically.")


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 1")
print("=" * 70)
print("1. CPython is the reference C implementation; its memory model uses reference counting + GC.")
print("2. ALL Python objects live on the private heap. The call stack holds variable references.")
print("3. Every object has a PyObject header containing ob_refcnt (8 bytes) and ob_type (8 bytes).")
print("4. Python optimizes small allocations (<= 512 bytes) with pymalloc to avoid OS overhead.")
print("=" * 70)
