# Lesson 10: Iterators and Generators

**Author**: Navneet Saunee  
**Date**: November 2026  

Reference and interactive demo script covering Python iterators, the iterator protocol, custom iterators, generators, `yield`, generator expressions, `yield from`, advanced generator methods (`send()`, `close()`), lazy evaluation, memory efficiency, practical streaming patterns, and essential interview questions.

---

## 1. Introduction

In Python, efficient data handling and sequence iteration are powered by **iterables**, **iterators**, and **generators**. Understanding these concepts allows you to write clean, Pythonic code that processes massive or infinite datasets with minimal memory overhead through **lazy evaluation**.

### Key Distinctions
- **Iterable**: An object that can return an iterator. It implements `__iter__()` (or `__getitem__()`). Examples include `list`, `dict`, `str`, `tuple`, and `set`.
- **Iterator**: A stateful object representing a data stream. It implements both `__iter__()` (which returns `self`) and `__next__()` (which returns the next item or raises `StopIteration`).
- **Generator**: A concise, memory-efficient way to implement an iterator using functions containing the `yield` keyword or parenthesized generator expressions `(...)`.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain the distinction between an **iterable** and an **iterator** in Python.
2. Manually step through iteration using `iter()`, `next()`, and sentinel default values.
3. Understand the **Iterator Protocol** (`__iter__()`, `__next__()`) and how `for` loops consume sequences.
4. Implement **custom iterator classes** with robust state handling and `StopIteration`.
5. Write **generator functions** with `yield` to create lazy sequences.
6. Use **generator expressions** as memory-efficient drop-in replacements for list comprehensions.
7. Flatten nested structures and delegate generation using `yield from`.
8. Communicate bidirectionally with generators using `.send()`, `.close()`, and `.throw()`.
9. Measure and demonstrate **lazy evaluation** and **memory efficiency** on large datasets.
10. Build modular **streaming pipelines** for log processing and data batching/chunking.
11. Confidently answer popular technical interview questions on iterators and generators.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Learning Sequence & Concepts](#4-learning-sequence--concepts)
  - [4.1 Iterable vs. Iterator](#41-iterable-vs-iterator)
  - [4.2 The Iterator Protocol & StopIteration](#42-the-iterator-protocol--stopiteration)
  - [4.3 Creating Custom Iterators](#43-creating-custom-iterators)
  - [4.4 Generators & the `yield` Keyword](#44-generators--the-yield-keyword)
  - [4.5 Generator Expressions](#45-generator-expressions)
  - [4.6 Delegating with `yield from`](#46-delegating-with-yield-from)
  - [4.7 Advanced Generator Methods (`send`, `close`, `throw`)](#47-advanced-generator-methods-send-close-throw)
  - [4.8 Lazy Evaluation & Memory Efficiency](#48-lazy-evaluation--memory-efficiency)
  - [4.9 Practical Stream Pipelines](#49-practical-stream-pipelines)
- [5. Code Examples](#5.code-examples)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. Learning Sequence & Concepts

### 4.1 Iterable vs. Iterator

| Concept | What it is | Methods | Example |
| :--- | :--- | :--- | :--- |
| **Iterable** | Any object capable of returning its members one by one | `__iter__()` | `[1, 2, 3]`, `"hello"`, `{"a": 1}` |
| **Iterator** | Stateful stream object that produces items on demand | `__iter__()` and `__next__()` | `iter([1, 2, 3])`, generator objects |

```python
numbers = [1, 2, 3]          # Iterable
it = iter(numbers)           # Iterator
print(next(it))              # 1
print(next(it))              # 2
print(next(it))              # 3
print(next(it, "default"))   # 'default' (avoids StopIteration)
```

### 4.2 The Iterator Protocol & StopIteration

When you run `for item in sequence:`, Python under the hood executes:
1. `iterator = iter(sequence)` (calls `sequence.__iter__()`)
2. Repeatedly calls `item = next(iterator)` (calls `iterator.__next__()`)
3. When elements run out, `__next__()` raises `StopIteration`, which `for` catches cleanly to stop.

### 4.3 Creating Custom Iterators

To make a custom class an iterator, implement two dunder methods:
- `__iter__(self)`: Returns `self`.
- `__next__(self)`: Returns the next item, or raises `StopIteration`.

```python
class CountDown:
    def __init__(self, start):
        self.count = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.count <= 0:
            raise StopIteration
        val = self.count
        self.count -= 1
        return val
```

### 4.4 Generators & the `yield` Keyword

A generator is a function containing one or more `yield` statements.
- Calling the function does not run the code immediately; it returns a generator object.
- When `next()` is called, execution advances until hitting `yield <value>`.
- The function state (local variables, instruction pointer) is frozen until `next()` is called again.

```python
def count_down_gen(start):
    while start > 0:
        yield start
        start -= 1
```

### 4.5 Generator Expressions

Generator expressions offer list comprehension syntax with lazy evaluation semantics:
```python
# List comprehension (eager, allocates entire list in memory)
squares_list = [x * x for x in range(1_000_000)]

# Generator expression (lazy, generates items on demand)
squares_gen = (x * x for x in range(1_000_000))
```

### 4.6 Delegating with `yield from`

`yield from <iterable>` delegates iteration to a sub-generator or iterable:
- Flattens nested structures cleanly without manual inner loops.
- Automatically handles bidirectional communication (`send`, `throw`, returns) between the caller and sub-generator.

```python
def flatten(items):
    for x in items:
        if isinstance(x, list):
            yield from flatten(x)
        else:
            yield x
```

### 4.7 Advanced Generator Methods (`send`, `close`, `throw`)

Generators can receive data using `.send(value)`:
- `.send(None)` or `next(gen)` **primes** the generator to reach the first `yield`.
- `received = yield current_val` yields `current_val` to the caller and assigns the incoming `.send()` value to `received`.
- `.close()` raises `GeneratorExit` inside the generator to terminate it cleanly.
- `.throw(ExceptionType)` raises an exception at the point of suspension.

### 4.8 Lazy Evaluation & Memory Efficiency

Instead of computing and storing a billion numbers in memory, generators compute each item only when requested:
- 1,000,000 integers in a list: **~8.4 MB**
- 1,000,000 integers in a generator: **~192 bytes** (over 40,000x less memory!)

### 4.9 Practical Stream Pipelines

Chain generators together like Unix pipes (`cat log | grep ERROR | awk ...`):
```python
logs = read_large_log_file("app.log")
errors = (line for line in logs if "ERROR" in line)
alerts = (format_alert(err) for err in errors)
for alert in alerts:
    send_webhook(alert)
```

---

## 5. Code Examples

All concepts are fully implemented and runnable in [iterators_and_generators.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson10_IteratorsAndGenerators/iterators_and_generators.py):
1. **Iterable vs. Iterator Inspection**: Comparing `dir()` attributes and types.
2. **Manual `for` Loop Simulation**: `while True` + `try/except StopIteration`.
3. **Custom Iterators**: `CountUpTo` and `FibonacciIterator`.
4. **Generator Functions**: Step-by-step state suspension with `yield`.
5. **Generator Expressions**: Memory comparisons and inline aggregation.
6. **Delegation**: `chain_sequences` and recursive `flatten` using `yield from`.
7. **Coroutines**: `running_accumulator` with `.send()` and `.close()`.
8. **Memory Benchmarking**: `sys.getsizeof` comparing list vs. generator.
9. **Streaming Log Pipeline & Data Chunking**: Lazy filtering and fixed-size chunking.

---

## 6. Frequently Asked Interview Questions

### Q1: What is the difference between an iterable, an iterator, and a generator?
**Answer**:
- An **iterable** is any object with `__iter__()` that can be looped over (e.g. lists, tuples, dicts).
- An **iterator** is an object with `__iter__()` and `__next__()` that preserves state and produces values on demand.
- A **generator** is a specialized function or expression using `yield` that Python automatically compiles into an iterator. All generators are iterators, and all iterators are iterables.

### Q2: Why does an iterator's `__iter__()` method return `self`?
**Answer**:
Iterators must themselves be iterable so they can be passed directly to `for` loops, `list()`, `sum()`, and other built-ins expecting an iterable. Returning `self` fulfills the iterator protocol:
```python
it = iter([1, 2, 3])
iter(it) is it  # True
```

### Q3: Can you iterate over a generator more than once?
**Answer**:
No. Generators are **exhaustible streams**. Once they produce their final item or raise `StopIteration`, subsequent calls will continue to raise `StopIteration`. To iterate again, you must instantiate a new generator object.

### Q4: What happens if `return` is used inside a generator function?
**Answer**:
In Python 3.3+, `return value` in a generator terminates iteration by raising `StopIteration(value)`. When delegated via `yield from`, that return value becomes the value of the `yield from` expression:
```python
result = yield from subgen()  # result gets the subgen's return value
```

### Q5: What is the purpose of `yield from` over a nested `for` loop?
**Answer**:
Beyond shorter code (`yield from subgen` vs `for item in subgen: yield item`), `yield from` establishes a transparent bidirectional channel. Calls to `.send()`, `.throw()`, and `.close()` on the delegating generator are passed directly through to the sub-generator.

### Q6: How does generator memory usage compare to lists?
**Answer**:
Lists allocate memory proportional to $O(N)$ elements upfront. Generators use $O(1)$ memory regardless of sequence length because only the current value and execution state are held in memory.

---

## 7. How to Run

Run the lesson script directly from terminal:
```bash
python iterators_and_generators.py
```

---

## 8. Exercises

At the bottom of [iterators_and_generators.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson10_IteratorsAndGenerators/iterators_and_generators.py):
1. **Custom Even Range Iterator**: Implement `EvenRange(start, stop)` that yields even numbers within the range.
2. **Prime Number Generator**: Write a generator `prime_generator(limit)` that lazily yields primes up to `limit`.
3. **Filtering Generator Expression**: Filter a list of strings for lengths $> 5$ and uppercase them.
4. **Streaming Pipeline**: Build a two-stage generator pipeline calculating a running average.
5. **Iterator Self-Identity Verification**: Verify with `id()` that `iter(iterator) is iterator`.

---

## 9. Completion Checklist

- [ ] Run `python iterators_and_generators.py` and inspect all module outputs.
- [ ] Understand the difference between `__iter__` and `__next__`.
- [ ] Implement exercise 1 (`EvenRange`).
- [ ] Implement exercise 2 (`prime_generator`).
- [ ] Implement exercise 3 (filtering generator expression).
- [ ] Implement exercise 4 (running average pipeline).
- [ ] Review all interview questions and answers.
