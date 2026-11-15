# Lesson 17: Context Managers and the `with` Statement in Python

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering Python's Context Management protocol and the `with` statement. Learn class-based context managers (`__enter__`, `__exit__`), exception handling and suppression, generator-based context managers using `@contextlib.contextmanager`, standard library helpers (`suppress`, `ExitStack`), and resource lifecycle patterns.

---

## 1. Introduction

Managing external resources (open files, network sockets, database connections, locks) requires guaranteed cleanup regardless of whether code succeeds or crashes with an unhandled exception.

Before context managers, Python developers used verbose `try/finally` blocks. The `with` statement encapsulates acquisition and release logic directly within reusable **Context Managers**.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain the motivation for context managers over explicit `try/finally` blocks.
2. Implement class-based context managers with `__enter__()` and `__exit__()`.
3. Handle, inspect, and conditionally suppress exceptions inside `__exit__()`.
4. Create concise generator-based context managers using `@contextlib.contextmanager`.
5. Use `contextlib.suppress()` to cleanly ignore expected exceptions.
6. Manage dynamic numbers of resources simultaneously using `contextlib.ExitStack`.
7. Understand asynchronous context managers (`__aenter__` and `__aexit__`).
8. Confidently answer technical interview questions regarding context managers.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Context Manager Concepts](#4-core-context-manager-concepts)
  - [4.1 The `with` Statement Mechanics](#41-the-with-statement-mechanics)
  - [4.2 The Class Protocol: `__enter__` and `__exit__`](#42-the-class-protocol-__enter__-and-__exit__)
  - [4.3 Exception Handling and Suppression in `__exit__`](#43-exception-handling-and-suppression-in-__exit__)
  - [4.4 Generator Context Managers (`@contextmanager`)](#44-generator-context-managers-contextmanager)
  - [4.5 `contextlib` Utilities (`suppress`, `ExitStack`)](#45-contextlib-utilities-suppress-exitstack)
- [5. Frequently Asked Interview Questions](#5-frequently-asked-interview-questions)
- [6. How to Run](#6-how-to-run)
- [7. Exercises](#7-exercises)
- [8. Completion Checklist](#8-completion-checklist)

---

## 4. Core Context Manager Concepts

### 4.1 The `with` Statement Mechanics
When Python enters a `with expr as target:` statement:
1. It evaluates `expr` to obtain the context manager object.
2. It calls `__enter__()` on the object.
3. The value returned by `__enter__()` is assigned to `target`.
4. The code block executes.
5. `__exit__()` is called upon exit, even if an exception was raised inside the block.

### 4.2 The Class Protocol: `__enter__` and `__exit__`
```python
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start
        return False  # Do not suppress exceptions
```

### 4.3 Exception Handling and Suppression in `__exit__`
`__exit__` receives three arguments if an exception occurred:
- `exc_type`: The exception class (e.g. `ValueError`)
- `exc_val`: The exception instance
- `exc_tb`: The traceback object

If no exception occurred, all three are `None`.
> **Suppression Rule**: If `__exit__()` returns `True`, Python **suppresses** the exception and continues execution normally. If it returns `False` (or `None`), the exception is re-raised.

### 4.4 Generator Context Managers (`@contextmanager`)
Avoid writing boilerplate classes using the `@contextmanager` decorator:
```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    # Setup (__enter__)
    resource = acquire_resource()
    try:
        yield resource  # Passed to 'as target'
    finally:
        # Teardown (__exit__)
        resource.release()
```

### 4.5 `contextlib` Utilities
- **`suppress(*exceptions)`**: Silently catches and ignores specified exceptions:
  ```python
  with suppress(FileNotFoundError):
      os.remove("missing.txt")
  ```
- **`ExitStack`**: Dynamically enters an arbitrary number of context managers (e.g., opening all files matching a glob):
  ```python
  with ExitStack() as stack:
      files = [stack.enter_context(open(fname)) for fname in file_list]
  ```

---

## 5. Frequently Asked Interview Questions

### Q1: What are the parameters passed to `__exit__()` and what does returning `True` mean?
**Answer**:
The three parameters are `(exc_type, exc_val, exc_tb)`. If an exception was raised within the `with` block, these contain the exception details; otherwise they are `None`. Returning `True` from `__exit__()` instructs Python that the exception was handled, suppressing it from propagating up the call stack.

### Q2: What is the advantage of `@contextlib.contextmanager` over writing a class?
**Answer**:
It significantly reduces boilerplate code. Instead of creating a class with state tracking, `__enter__`, and `__exit__`, you can write a simple generator function with a standard `try...finally` block. Everything before `yield` runs on entry, and the `finally` block runs on exit.

### Q3: How do multiple context managers behave in a single `with` statement?
**Answer**:
Writing `with A() as a, B() as b:` nests the managers from left to right. It is equivalent to:
```python
with A() as a:
    with B() as b:
        ...
```
`B.__exit__()` executes first, followed by `A.__exit__()`.

---

## 6. How to Run

Run the script from your terminal:
```bash
python context_managers.py
```

---

## 7. Exercises

In [context_managers.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson17_ContextManagers/context_managers.py):
1. **HTML Tag Wrapper**: Create a class context manager printing `<tag>` on enter and `</tag>` on exit.
2. **Generator Logger**: Write a `@contextmanager` function logging `START: <name>` and `END: <name>`.
3. **Custom Exception Suppressor**: Implement a class context manager that catches and suppresses only `KeyError`.
4. **ExitStack Management**: Use `ExitStack` to manage multiple simultaneous file handles.

---

## 8. Completion Checklist

- [ ] Run `python context_managers.py` and review output.
- [ ] Understand the 3 arguments of `__exit__` and return value suppression rules.
- [ ] Complete exercise 1 (HTML Tag class context manager).
- [ ] Complete exercise 2 (@contextmanager generator).
- [ ] Complete exercise 3 (KeyError suppression).
- [ ] Complete exercise 4 (ExitStack multi-resource).
- [ ] Review all interview questions.
