"""
================================================================================
Topic 4: Object References and Copying
================================================================================

RELATABLE ANALOGY:
    Think of documents:
    - ASSIGNMENT (`b = a`): Two people looking at the EXACT same paper on a desk.
      If person A writes on it, person B sees the writing immediately.
    - SHALLOW COPY (`copy.copy(a)`): Photocopying only the folder jacket, but
      leaving the original papers inside. If you change a paper inside, both see it!
    - DEEP COPY (`copy.deepcopy(a)`): Making a complete photocopy of the folder AND
      every single sheet of paper inside. Completely separate and independent!

CONCEPTS COVERED:
    1. Variable Assignment vs Object Duplication.
    2. Shared References and the Aliasing Trap on Mutable Objects.
    3. Shallow Copy (`copy.copy()`, `lst[:]`, `dict.copy()`):
       - Duplicates the outer container.
       - Shares the inner child element pointers!
    4. Deep Copy (`copy.deepcopy()`):
       - Recursively duplicates every nested object into new memory addresses.
       - The Memo dictionary: How deepcopy handles circular self-referencing graphs.
    5. Practical demonstrations with nested lists and custom classes.
================================================================================
"""

import copy

print("=" * 70)
print("TOPIC 4: Object References and Copying")
print("=" * 70)


# ==============================================================================
# SECTION 1: Assignment vs Shallow vs Deep Copy Summary
# ==============================================================================
"""
Operation               Outer Container Address     Inner Elements Address
-------------------------------------------------------------------------------
Assignment (b = a)      SAME as 'a'                 SAME as 'a' (Zero duplication)
Shallow (copy.copy(a))  NEW unique address          SAME as 'a' (Shared inner pointers!)
Deep (copy.deepcopy(a)) NEW unique address          NEW unique addresses (Full clone)
"""


# ==============================================================================
# SECTION 2: Shallow Copy & The Shared Inner Pointer Trap
# ==============================================================================
print("\n--- 1. Shallow Copy: Shared Inner Pointers ---")

original_matrix = [[10, 20], [30, 40]]

# Step 1: Create a shallow copy using copy.copy (or original_matrix[:])
shallow_matrix = copy.copy(original_matrix)

print(f"original_matrix address: {hex(id(original_matrix))}")
print(f"shallow_matrix address : {hex(id(shallow_matrix))} (Different outer container!)")

# Step 2: Check inner element memory addresses:
print("\nChecking inner list memory addresses:")
print(f"original[0] address    : {hex(id(original_matrix[0]))}")
print(f"shallow[0] address     : {hex(id(shallow_matrix[0]))} (IDENTICAL inner list!)")

# Step 3: Mutate inner element through the shallow copy:
print("\nMutating shallow_matrix[0].append(99):")
shallow_matrix[0].append(99)

print(f"  original_matrix : {original_matrix} (UNINTENTIONALLY MUTATED!)")
print(f"  shallow_matrix  : {shallow_matrix}")


# ==============================================================================
# SECTION 3: Deep Copy: Complete Memory Isolation
# ==============================================================================
print("\n--- 2. Deep Copy: Complete Memory Isolation ---")

clean_matrix = [[10, 20], [30, 40]]
deep_matrix = copy.deepcopy(clean_matrix)

print(f"clean_matrix address : {hex(id(clean_matrix))}")
print(f"deep_matrix address  : {hex(id(deep_matrix))} (Different outer container)")

print(f"clean[0] address     : {hex(id(clean_matrix[0]))}")
print(f"deep[0] address      : {hex(id(deep_matrix[0]))} (BRAND NEW inner list!)")

# Mutate inner element in deep copy:
print("\nMutating deep_matrix[0].append(999):")
deep_matrix[0].append(999)

print(f"  clean_matrix : {clean_matrix} (SAFE & PRESERVED!)")
print(f"  deep_matrix  : {deep_matrix}")


# ==============================================================================
# SECTION 4: Copying Custom Class Instances
# ==============================================================================
print("\n--- 3. Copying Custom Class Instances ---")


class Department:
    def __init__(self, name: str):
        self.name = name


class Employee:
    def __init__(self, emp_name: str, dept: Department):
        self.emp_name = emp_name
        self.dept = dept


sales_dept = Department("Enterprise Sales")
emp1 = Employee("Navneet", sales_dept)

# Shallow copy vs Deep copy of employee
emp_shallow = copy.copy(emp1)
emp_deep = copy.deepcopy(emp1)

print(f"emp1 department address       : {hex(id(emp1.dept))}")
print(f"emp_shallow department address: {hex(id(emp_shallow.dept))} (Shared!)")
print(f"emp_deep department address   : {hex(id(emp_deep.dept))} (Isolated clone!)")

# Mutating department through shallow copy
emp_shallow.dept.name = "Global Strategy"
print(f"\nAfter mutating department on emp_shallow:")
print(f"  emp1 department name: '{emp1.dept.name}' (Affected!)")
print(f"  emp_deep dept name  : '{emp_deep.dept.name}' (Unaffected)")


# ==============================================================================
# SECTION 5: How Deepcopy Handles Cycles (The Memo Dictionary)
# ==============================================================================
print("\n--- 4. Deepcopy on Self-Referencing Objects ---")
"""
If an object contains a reference to itself, why doesn't `copy.deepcopy()`
infinitely recurse and crash with a RecursionError?
Because `deepcopy` maintains an internal `memo` dictionary of:
{id(original_object): cloned_object}
When it encounters an object it already cloned, it reuses the clone!
"""

cyclic_list = [1, 2]
cyclic_list.append(cyclic_list)  # Index 2 points to cyclic_list itself

cloned_cyclic = copy.deepcopy(cyclic_list)
print("Deepcopy of self-referencing list succeeded without crashing!")
print(f"cloned_cyclic[2] is cloned_cyclic? -> {cloned_cyclic[2] is cloned_cyclic}")
print(f"cloned_cyclic is cyclic_list?       -> {cloned_cyclic is cyclic_list} (Different object)")


# ==============================================================================
# INTERVIEW QUESTIONS FOR TOPIC 4
# ==============================================================================
print("\n" + "=" * 70)
print("INTERVIEW QUESTIONS - Topic 4")
print("=" * 70)
print("Q1: What is the difference between a shallow copy and a deep copy?")
print("A1: A shallow copy constructs a new compound object and inserts references to the")
print("    original objects. A deep copy recursively constructs copies of everything inside.")
print("\nQ2: How does copy.deepcopy handle cyclic data structures without infinite loops?")
print("A2: It maintains an internal `memo` dictionary mapping original object IDs to their")
print("    new copies, returning the cached copy if an object is re-encountered.")
print("=" * 70)
