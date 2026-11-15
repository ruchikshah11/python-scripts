"""
================================================================================
Topic 5: Object Copying (Assignment vs Shallow Copy vs Deep Copy)
================================================================================

SYNOPSIS:
    Deep dive into memory mechanics during object copying. Clarifies the difference
    between variable assignment (pointer sharing), shallow copy (copying outer container,
    sharing inner elements), and deep copy (recursively duplicating the entire object graph).
    Uses the `copy` module (`copy.copy`, `copy.deepcopy`), slicing (`[:]`), and factory constructors.

CONCEPTS COVERED:
    1. Assignment (`=`) vs Copying: Rebinding names vs duplicating objects.
    2. Shallow Copy:
       - Outer container has a new memory address.
       - Inner elements still share identical memory addresses!
       - Methods: `copy.copy()`, slicing `lst[:]`, `list(lst)`, `dict.copy()`.
    3. Deep Copy:
       - Recursively duplicates every child object.
       - Completely isolated memory tree.
       - Handling self-referential / cyclic structures with memo dictionary.
    4. Practical Demonstrations:
       - Mutating nested lists and observing side effects.
       - Copying custom class instances.

EXPECTED OUTPUT HIGHLIGHTS:
    - Address comparisons demonstrating shared inner pointers in shallow copies.
    - True memory isolation achieved through deep copying.
    - Preserved circular links without infinite recursion during deepcopy.
================================================================================
"""

import copy

print("=" * 70)
print("TOPIC 5: Object Copying (Assignment vs Shallow vs Deep Copy)")
print("=" * 70)


# ==============================================================================
# SECTION 1: Summary of the 3 Operations
# ==============================================================================
"""
Operation               Outer Container Address     Inner Elements Address
-------------------------------------------------------------------------------
Assignment (b = a)      SAME as 'a'                 SAME as 'a' (Zero duplication)
Shallow (copy.copy(a))  NEW unique address          SAME as 'a' (Shared inner pointers!)
Deep (copy.deepcopy(a)) NEW unique address          NEW unique addresses (Full clone)
"""


# ==============================================================================
# SECTION 2: Assignment vs Shallow Copy with Nested Lists
# ==============================================================================
print("\n--- 1. Shallow Copy: Shared Inner Pointers ---")

original_matrix = [[10, 20], [30, 40]]

# 1. Assignment:
alias_matrix = original_matrix

# 2. Shallow Copy using copy.copy (or original_matrix[:]):
shallow_matrix = copy.copy(original_matrix)

print(f"original_matrix addr: {hex(id(original_matrix))}")
print(f"alias_matrix addr   : {hex(id(alias_matrix))} (IDENTICAL pointer)")
print(f"shallow_matrix addr : {hex(id(shallow_matrix))} (NEW container address)")

print("\nInner element memory inspection:")
print(f"original[0] addr    : {hex(id(original_matrix[0]))}")
print(f"shallow[0]  addr    : {hex(id(shallow_matrix[0]))} (IDENTICAL inner list!)")

# Modifying inner nested list:
print("\nMutating shallow_matrix[0].append(99):")
shallow_matrix[0].append(99)

print(f"  original_matrix : {original_matrix} (UNINTENDED MUTATION!)")
print(f"  shallow_matrix  : {shallow_matrix}")


# ==============================================================================
# SECTION 3: Deep Copy: Complete Memory Isolation
# ==============================================================================
print("\n--- 2. Deep Copy: True Memory Isolation ---")

clean_matrix = [[10, 20], [30, 40]]
deep_matrix = copy.deepcopy(clean_matrix)

print(f"clean_matrix addr : {hex(id(clean_matrix))}")
print(f"deep_matrix addr  : {hex(id(deep_matrix))} (NEW container address)")

print(f"clean[0] addr     : {hex(id(clean_matrix[0]))}")
print(f"deep[0]  addr     : {hex(id(deep_matrix[0]))} (NEW inner list address!)")

# Mutating deep copy inner list:
print("\nMutating deep_matrix[0].append(999):")
deep_matrix[0].append(999)

print(f"  clean_matrix : {clean_matrix} (PRESERVED & SAFE!)")
print(f"  deep_matrix  : {deep_matrix}")


# ==============================================================================
# SECTION 4: Copying Custom Classes
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

# Shallow copy of employee:
emp_shallow = copy.copy(emp1)
# Deep copy of employee:
emp_deep = copy.deepcopy(emp1)

print(f"emp1 department address       : {hex(id(emp1.dept))}")
print(f"emp_shallow department address: {hex(id(emp_shallow.dept))} (Shared!)")
print(f"emp_deep department address   : {hex(id(emp_deep.dept))} (Independent clone!)")

# Mutate department through shallow copy:
emp_shallow.dept.name = "Global Strategy"
print(f"\nAfter mutating department on emp_shallow:")
print(f"  emp1 department name: '{emp1.dept.name}' (Affected!)")
print(f"  emp_deep dept name  : '{emp_deep.dept.name}' (Unaffected)")


# ==============================================================================
# SECTION 5: How Deepcopy Handles Cycles (The Memo Dictionary)
# ==============================================================================
print("\n--- 4. Deepcopy and Circular References (The Memo Dictionary) ---")
"""
If an object points to itself, how does copy.deepcopy() avoid an infinite loop?
It internally maintains a `memo` dictionary of {original_object_id: copied_object}.
When it encounters an object it has already cloned, it returns the cloned reference!
"""

cyclic_list = [1, 2]
cyclic_list.append(cyclic_list)  # Index 2 points back to cyclic_list itself

cloned_cyclic = copy.deepcopy(cyclic_list)
print("Deepcopy of self-referencing list succeeded without crashing!")
print(f"cloned_cyclic[2] is cloned_cyclic? -> {cloned_cyclic[2] is cloned_cyclic}")
print(f"cloned_cyclic is cyclic_list?       -> {cloned_cyclic is cyclic_list} (Different object)")


# ==============================================================================
# SUMMARY & KEY TAKEAWAYS
# ==============================================================================
print("\n" + "=" * 70)
print("KEY TAKEAWAYS - Topic 5")
print("=" * 70)
print("1. Assignment (=) only copies the reference pointer; zero objects are duplicated.")
print("2. Shallow copy duplicates the outermost container, but leaves inner objects shared.")
print("3. Deep copy recursively duplicates all child objects, creating a separate memory tree.")
print("4. Use shallow copies for flat, non-nested collections to save CPU and RAM.")
print("5. Use deep copies when modifying nested mutable data structures.")
print("=" * 70)
