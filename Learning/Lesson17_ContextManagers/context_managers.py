"""
SYNOPSIS
    Lesson 17: Context Managers and the `with` Statement in Python -
    Resource allocation/deallocation, the context management protocol
    (__enter__ and __exit__), exception handling and suppression in __exit__,
    generator-based context managers with @contextlib.contextmanager,
    standard library utilities (contextlib.suppress, ExitStack, redirect_stdout),
    reentrant context managers, and async context managers (__aenter__, __aexit__).

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python context_managers.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import os
import sys
import time
from contextlib import contextmanager, suppress, ExitStack

print("=" * 60)
print("LESSON 17: Context Managers and the 'with' Statement in Python")
print("=" * 60)


# ============================================================
# 1. Why Context Managers? The 'with' Statement
# ============================================================
print("\n--- 1. Why Context Managers? Automatic Resource Management ---")
# Without a context manager, resources like open files, DB locks, or sockets
# must be closed inside a try/finally block to guarantee cleanup if an error occurs.
# The 'with' statement automates setup and teardown cleanly.

sample_path = "temp_demo_file.txt"

# Traditional cumbersome pattern:
f = open(sample_path, "w")
try:
    f.write("Hello from try/finally!\n")
finally:
    f.close()

# Pythonic context manager pattern:
with open(sample_path, "a") as f:
    f.write("Appended safely using 'with' statement!\n")

print(f"File closed automatically? {f.closed}")
if os.path.exists(sample_path):
    os.remove(sample_path)


# ============================================================
# 2. Class-Based Context Managers: __enter__ and __exit__
# ============================================================
print("\n--- 2. Class-Based Protocol: __enter__ and __exit__ ---")


class PerformanceTimer:
    """Measures execution time of a code block."""

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.start_time = None
        self.elapsed = 0.0

    def __enter__(self):
        print(f"  [Timer: '{self.task_name}'] Started...")
        self.start_time = time.time()
        return self  # Bound to variable in 'as <target>'

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        print(f"  [Timer: '{self.task_name}'] Finished in {self.elapsed:.4f}s.")
        # Returning False (or None) propagates any exception that occurred inside 'with'
        # Returning True suppresses the exception
        return False


with PerformanceTimer("Heavy computation") as timer:
    total = sum(x * x for x in range(200_000))

print(f"Total computed: {total}, Timer instance recorded: {timer.elapsed:.4f}s")


# ============================================================
# 3. Exception Handling & Suppression in __exit__
# ============================================================
print("\n--- 3. Handling and Suppressing Exceptions in __exit__ ---")


class SafeDatabaseTransaction:
    """Simulates a database transaction with automatic commit/rollback."""

    def __enter__(self):
        print("  [DB] BEGIN TRANSACTION")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"  [DB] ROLLBACK due to error: {exc_val}")
            # Suppress specific error by returning True
            if issubclass(exc_type, ValueError):
                print("  [DB] Suppressing ValueError cleanly.")
                return True
        else:
            print("  [DB] COMMIT TRANSACTION")
        return False


print("Successful transaction:")
with SafeDatabaseTransaction():
    print("  Executing valid SQL updates...")

print("\nFailed transaction with error suppression:")
with SafeDatabaseTransaction():
    print("  Executing bad transaction...")
    raise ValueError("Invalid user foreign key ID")

print("Execution safely continued after suppressed exception!")


# ============================================================
# 4. Generator-Based: @contextlib.contextmanager
# ============================================================
print("\n--- 4. Generator-Based Context Managers (@contextmanager) ---")
# The @contextmanager decorator lets you build a context manager out of a generator.
# Everything before 'yield' is __enter__(); the yielded value is 'as target';
# everything after 'yield' is __exit__().


@contextmanager
def temporary_working_directory(temp_dir_name: str):
    """Safely creates and cleans up a temporary scratch directory."""
    print(f"  [Setup] Creating temporary workspace '{temp_dir_name}'...")
    os.makedirs(temp_dir_name, exist_ok=True)
    try:
        # yield transfers execution to the 'with' block body
        yield os.path.abspath(temp_dir_name)
    finally:
        # Guaranteed cleanup, even if an unhandled error occurred
        print(f"  [Teardown] Removing temporary workspace '{temp_dir_name}'...")
        if os.path.exists(temp_dir_name):
            os.rmdir(temp_dir_name)


with temporary_working_directory("temp_scratch_workspace") as workspace_path:
    print(f"  Inside 'with' block: working in {workspace_path}")


# ============================================================
# 5. Standard Library Helpers (contextlib: suppress, ExitStack)
# ============================================================
print("\n--- 5. Standard Library Helpers: suppress & ExitStack ---")

# 1. contextlib.suppress: cleaner replacement for empty `except Exception: pass`
print("Using contextlib.suppress(FileNotFoundError):")
with suppress(FileNotFoundError):
    os.remove("non_existent_file_xyz_123.tmp")
print("  Successfully suppressed FileNotFoundError without crashing!")

# 2. contextlib.ExitStack: dynamically manage multiple context managers
filenames = ["temp_file_1.txt", "temp_file_2.txt"]
with ExitStack() as stack:
    # Dynamically open all files in a variable-length list
    opened_files = [stack.enter_context(open(fn, "w")) for fn in filenames]
    for idx, fh in enumerate(opened_files):
        fh.write(f"Data from file {idx + 1}\n")
    print(f"  Opened {len(opened_files)} files dynamically with ExitStack.")

# Clean up temp files
for fn in filenames:
    if os.path.exists(fn):
        os.remove(fn)


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python context_managers.py
# ============================================================
#
# 1. CUSTOM CLASS CONTEXT MANAGER:
#    Build a class `HtmlTag(tag_name)` that prints `<tag_name>` on entry
#    and `</tag_name>` on exit.
#    Use it to wrap a print statement: `with HtmlTag("div"): print("  Hello World")`.
#
# 2. GENERATOR CONTEXT MANAGER:
#    Use `@contextmanager` to write `custom_logger(title)` that logs
#    `"START: <title>"` on entry and `"END: <title>"` on exit.
#
# 3. EXCEPTION SUPPRESSION:
#    Implement a context manager `IgnoreKeyErrors()` using a class with `__exit__`
#    that suppresses `KeyError` exceptions occurring inside the block.
#
# 4. EXITSTACK MULTI-RESOURCE MANAGEMENT:
#    Use `ExitStack` to open two file objects safely and copy contents from
#    one to another.

# --- write your code below this line ---
