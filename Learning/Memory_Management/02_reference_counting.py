"""
================================================================================
Topic 2: Reference Counting in CPython
================================================================================

RELATABLE ANALOGY:
    Think of reference counting like a library book:
    - Every person who checks out or reserves the book adds a tally mark.
    - When someone returns the book, a tally mark is erased.
    - When zero people have the book checked out, the library shelves or recycles it!

CONCEPTS COVERED:
    1. How CPython Tracks References (`ob_refcnt` in PyObject).
    2. Actions that INCREMENT reference count:
       - Assigning to a variable (`b = a`)
       - Adding to a collection (`lst.append(a)`)
       - Passing as an argument to a function (`func(a)`)
    3. Actions that DECREMENT reference count:
       - Deleting a variable with `del a`
       - Reassigning a variable (`a = None`)
       - Removing from a container (`lst.pop()`)
       - A function finishing and popping its call frame
    4. The `sys.getrefcount()` Quirk Explained (+1 temporary reference).
    5. Immediate Deallocation when refcount reaches 0.

PYTHON SPEC VS CPYTHON IMPLEMENTATION:
    - Python Specification: Unreachable objects are eventually collected automatically.
    - CPython Detail: Immediate reclamation via reference counting is a CPython feature!
      Other Pythons (Jython, PyPy) do not use reference counting.
================================================================================
"""

import sys
import ctypes

print("=" * 70)
print("TOPIC 2: Reference Counting in CPython")
print("=" * 70)


# ==============================================================================
# SECTION 1: How Reference Counting Works
# ==============================================================================
print("\n--- 1. How CPython Tracks References ---")
"""
In CPython, every object struct has an `ob_refcnt` counter.
- Whenever a new reference is created: CPython calls `Py_INCREF(op)`.
- Whenever a reference is dropped:     CPython calls `Py_DECREF(op)`.
- When `ob_refcnt == 0`:
  CPython immediately invokes the object's `tp_dealloc` function and frees the memory.
"""


class ResourceTracker:
    """Helper class that logs its creation and destruction."""

    def __init__(self, name: str):
        self.name = name
        print(f"  [ALLOCATED] '{self.name}' at address {hex(id(self))}")

    def __del__(self):
        # NOTE: __del__ is called immediately when refcount reaches zero
        print(f"  [DEALLOCATED] '{self.name}' at address {hex(id(self))} (refcount reached 0!)")


# ==============================================================================
# SECTION 2: The sys.getrefcount() Quirk
# ==============================================================================
print("\n--- 2. The sys.getrefcount() Quirk Explained ---")
"""
IMPORTANT ACCURACY NOTE:
Why does `sys.getrefcount(x)` always return 1 higher than you expect?

When you call `sys.getrefcount(target)`:
1. `target` is passed AS AN ARGUMENT into `getrefcount()`.
2. This argument binding creates a TEMPORARY REFERENCE inside the function call frame!
3. Therefore, `sys.getrefcount(x)` always counts the temporary parameter (+1).
"""

probe = ResourceTracker("TestSubject")

# probe is currently referenced by 1 variable: 'probe'
# But sys.getrefcount reports 2!
print(f"sys.getrefcount(probe) : {sys.getrefcount(probe)} (1 real variable + 1 temporary function argument)")


def read_raw_refcount_c(address: int) -> int:
    """Reads ob_refcnt directly from the C PyObject memory struct without parameter overhead."""
    return ctypes.c_ssize_t.from_address(address).value


print(f"Raw C struct refcount  : {read_raw_refcount_c(id(probe))} (True internal count: exactly 1!)")


# ==============================================================================
# SECTION 3: Step-by-Step Reference Count Tracking
# ==============================================================================
print("\n--- 3. Tracking Increments and Decrements ---")

print(f"Starting raw count      : {read_raw_refcount_c(id(probe))}")

# Increment 1: Variable assignment
alias = probe
print(f"After 'alias = probe'   : {read_raw_refcount_c(id(probe))} (Increased to 2)")

# Increment 2: Container storage
basket = [probe]
print(f"After 'basket = [probe]': {read_raw_refcount_c(id(probe))} (Increased to 3)")

# Increment 3: Function parameter
def demo_func(arg):
    print(f"  Inside function call  : {read_raw_refcount_c(id(arg))} (Increased to 4 by 'arg')")

demo_func(probe)
print(f"After function returns  : {read_raw_refcount_c(id(probe))} (Dropped back to 3)")

# Decrement 1: Clear container
basket.clear()
print(f"After 'basket.clear()'  : {read_raw_refcount_c(id(probe))} (Decreased to 2)")

# Decrement 2: Delete alias
del alias
print(f"After 'del alias'       : {read_raw_refcount_c(id(probe))} (Decreased to 1)")


# ==============================================================================
# SECTION 4: The 'del' Statement & Immediate Destruction
# ==============================================================================
print("\n--- 4. What 'del' Actually Does ---")
"""
COMMON MISCONCEPTION:
"'del x' deletes the object from memory."
--> FALSE! 'del x' deletes the NAME/VARIABLE 'x'.
    The object is ONLY destroyed if removing that name causes its
    reference count to drop to ZERO!
"""

print("Executing 'del probe' (the last remaining reference):")
# Dropping the final reference: count goes 1 -> 0 -> __del__ triggers immediately!
del probe
print("Execution continues past 'del probe'.")


# ==============================================================================
# SECTION 5: Scope Exit Cleanup
# ==============================================================================
print("\n--- 5. Automatic Reclamation on Scope Exit ---")


def temporary_worker():
    print("  Entering temporary_worker()...")
    local_obj = ResourceTracker("LocalWorker")
    print("  Exiting temporary_worker()...")
    # local_obj reference is popped from stack frame; count drops to 0 immediately!


temporary_worker()
print("Function exited. LocalWorker was deallocated before this line printed.")


# ==============================================================================
# INTERVIEW QUESTIONS FOR TOPIC 2
# ==============================================================================
print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS - Topic 2")
print("=" * 70)
print("Q1: What happens under the hood when a reference count hits 0 in CPython?")
print("A1: CPython immediately calls the type's `tp_dealloc` slot. The memory block is")
print("    either returned to the pymalloc pool or system free(), and __del__ runs if defined.")
print("\nQ2: Why is sys.getrefcount() always +1 higher than the actual number of variables?")
print("A2: Because passing the object to sys.getrefcount() binds it to a function argument,")
print("    creating a temporary reference on the call stack for the duration of the call.")
print("=" * 70)
