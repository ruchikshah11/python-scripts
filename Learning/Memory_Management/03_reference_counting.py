"""
================================================================================
Topic 3: Reference Counting in CPython
================================================================================

SYNOPSIS:
    Deep dive into CPython's primary memory management system: Reference Counting.
    Examines ob_refcnt in C structs, actions that increment/decrement counts,
    sys.getrefcount() temporary references, scope exits, the 'del' statement,
    and immediate object deallocation.

CONCEPTS COVERED:
    1. Reference Counting Fundamentals in CPython.
    2. What INCREASES the Reference Count:
       - Assignment to variables
       - Insertion into containers (lists, dicts, tuples, sets)
       - Passing as arguments to functions
    3. What DECREASES the Reference Count:
       - Variable going out of local scope
       - Explicit deletion with 'del'
       - Variable reassignment
       - Removal from a container
    4. The sys.getrefcount() Quirk: Why it is always +1 higher than expected.
    5. The 'del' Statement: Deleting references vs deleting objects.
    6. Destructor Execution: The __del__ method and its caveats.

EXPECTED OUTPUT HIGHLIGHTS:
    - Step-by-step refcount tracking from creation to destruction.
    - Demonstrating that 'del' does NOT directly destroy objects; it only removes references.
    - Immediate invocation of __del__ the instant refcount hits zero.
================================================================================
"""

import sys
import ctypes

print("=" * 70)
print("TOPIC 3: Reference Counting in CPython")
print("=" * 70)


# ==============================================================================
# SECTION 1: How CPython Maintains Reference Counts
# ==============================================================================
print("\n--- 1. Reference Counting Mechanism ---")
"""
In CPython, every PyObject contains the `ob_refcnt` field.
Whenever an object is referenced, CPython executes Py_INCREF(op).
Whenever a reference is dropped, CPython executes Py_DECREF(op).
When ob_refcnt reaches 0:
    Python IMMEDIATELY calls the type's tp_dealloc function to free memory.
"""


class TrackedResource:
    """Helper class that announces its destruction via __del__."""

    def __init__(self, tag: str):
        self.tag = tag
        print(f"  [ALLOCATED] '{self.tag}' at address {hex(id(self))}")

    def __del__(self):
        print(f"  [tp_dealloc -> __del__] '{self.tag}' at {hex(id(self))} DEALLOCATED!")


# ==============================================================================
# SECTION 2: sys.getrefcount() and the +1 Quirk
# ==============================================================================
print("\n--- 2. The sys.getrefcount() Quirk Explained ---")
"""
CRITICAL ACCURACY REQUIREMENT:
Why is sys.getrefcount(obj) always 1 higher than you expect?

When you call `sys.getrefcount(my_obj)`:
The object `my_obj` is PASSED AS AN ARGUMENT to the getrefcount() function!
Passing it into getrefcount() binds the parameter name inside getrefcount,
which TEMPORARILY INCREMENTS the reference count by 1!
Once getrefcount() finishes, that temporary reference is destroyed.
"""

obj1 = TrackedResource("ProbeObject")

# At this point, only 'obj1' references the object.
# But sys.getrefcount(obj1) will report 2!
print(f"sys.getrefcount(obj1) : {sys.getrefcount(obj1)} (1 actual variable + 1 temporary function argument)")


# To read the raw C struct refcount without passing it into a Python function,
# we can read the memory directly with ctypes:
def get_raw_c_refcount(address: int) -> int:
    """Reads ob_refcnt directly from the C PyObject struct at the given address."""
    return ctypes.c_ssize_t.from_address(address).value


raw_count = get_raw_c_refcount(id(obj1))
print(f"Raw C struct ob_refcnt: {raw_count} (Pure reference count without Python parameter overhead)")


# ==============================================================================
# SECTION 3: Operations that Increase Reference Count
# ==============================================================================
print("\n--- 3. What Increases Reference Count ---")

print(f"Initial raw count of obj1: {get_raw_c_refcount(id(obj1))}")

# 1. New variable assignment
ref_alias = obj1
print(f"After 'ref_alias = obj1' : {get_raw_c_refcount(id(obj1))}")

# 2. Container insertion
container_list = [obj1]
print(f"After putting in list    : {get_raw_c_refcount(id(obj1))}")

# 3. Passing to a function
def inspect_inside_function(arg):
    print(f"  Inside function call   : {get_raw_c_refcount(id(arg))} (arg parameter added another reference)")

inspect_inside_function(obj1)
print(f"After function returns   : {get_raw_c_refcount(id(obj1))} (parameter dropped)")


# ==============================================================================
# SECTION 4: Operations that Decrease Reference Count & 'del'
# ==============================================================================
print("\n--- 4. What Decreases Reference Count & The 'del' Statement ---")
"""
COMMON MISCONCEPTION:
"The 'del my_var' statement deletes the object from memory."
--> FALSE! 'del my_var' deletes the VARIABLE NAME (reference binding).
    The object is ONLY deallocated if removing that reference causes its
    reference count to drop to ZERO!
"""

# Dropping container reference
container_list.clear()
print(f"After container_list.clear() : {get_raw_c_refcount(id(obj1))}")

# Dropping alias reference
del ref_alias
print(f"After 'del ref_alias'        : {get_raw_c_refcount(id(obj1))}")

print("Now dropping the final reference 'del obj1':")
# This final 'del' drops count from 1 to 0 -> immediate __del__ triggered!
del obj1


# ==============================================================================
# SECTION 5: Scope Exits & Immediate Reclamation
# ==============================================================================
print("\n--- 5. Automatic Reclamation on Scope Exit ---")


def temporary_computation():
    print("  Entering temporary_computation()...")
    local_resource = TrackedResource("ScopeWorker")
    print(f"  Working with {local_resource.tag} inside function...")
    # When this function returns, local_resource frame reference is destroyed
    print("  Exiting temporary_computation()...")


temporary_computation()
print("Execution continues in caller; resource was reclaimed immediately upon return.")


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 3")
print("=" * 70)
print("1. Reference counting is CPython's primary real-time memory management system.")
print("2. When ob_refcnt hits 0, deallocation is INSTANT (deterministic cleanup).")
print("3. sys.getrefcount() is always +1 higher due to the function call argument reference.")
print("4. 'del x' unbinds the name 'x'; it only frees the object if refcount reaches zero.")
print("5. Limitations: Reference counting CANNOT reclaim circular references! (See Topic 4).")
print("=" * 70)
