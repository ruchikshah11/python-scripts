# Lesson 13: Multithreading in Python (`threading` & `concurrent.futures`)

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering multithreading in Python. Learn thread lifecycle management (`Thread`, `start`, `join`, `daemon`), synchronization primitives (`Lock`, `RLock`, `Semaphore`, `Event`), the Global Interpreter Lock (GIL), thread-safe inter-thread communication (`queue.Queue`), modern pooling with `ThreadPoolExecutor`, and I/O-bound concurrency best practices.

---

## 1. Introduction

**Multithreading** enables a Python application to run multiple threads of execution within a single process. All threads share the same memory space, enabling fast data sharing but requiring careful synchronization to avoid race conditions.

### When to Use Multithreading:
- **I/O-Bound Workloads**: Web scraping, REST API requests, database queries, file reading/writing, and network socket communication.
- Python automatically releases the **Global Interpreter Lock (GIL)** during blocking I/O calls, allowing other threads to run concurrently and dramatically reducing total runtime.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Create and manage threads using `threading.Thread`, `.start()`, and `.join()`.
2. Understand the behavior and cleanup lifecycle of **daemon threads**.
3. Explain the mechanics of the **Global Interpreter Lock (GIL)** and why threads excel at I/O-bound tasks but not CPU-bound tasks.
4. Diagnose and prevent **race conditions** using `threading.Lock` and context managers (`with lock:`).
5. Coordinate concurrent thread access using `threading.Semaphore` and `threading.Event`.
6. Implement safe Producer-Consumer pipelines using `queue.Queue`.
7. Leverage high-level task parallelism using `concurrent.futures.ThreadPoolExecutor`.
8. Answer technical interview questions on multithreading and the GIL.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Multithreading Concepts](#4-core-multithreading-concepts)
  - [4.1 Thread Lifecycle: Creation, start, join](#41-thread-lifecycle-creation-start-join)
  - [4.2 Daemon Threads](#42-daemon-threads)
  - [4.3 The Global Interpreter Lock (GIL)](#43-the-global-interpreter-lock-gil)
  - [4.4 Race Conditions & Locks](#44-race-conditions--locks)
  - [4.5 Semaphores and Events](#45-semaphores-and-events)
  - [4.6 Thread-Safe Queues (`queue.Queue`)](#46-thread-safe-queues-queuequeue)
  - [4.7 Modern Thread Pools (`ThreadPoolExecutor`)](#47-modern-thread-pools-threadpoolexecutor)
- [5. Frequently Asked Interview Questions](#5-frequently-asked-interview-questions)
- [6. How to Run](#6-how-to-run)
- [7. Exercises](#7-exercises)
- [8. Completion Checklist](#8-completion-checklist)

---

## 4. Core Multithreading Concepts

### 4.1 Thread Lifecycle: Creation, start, join
```python
import threading
import time

def fetch_data():
    time.sleep(1)
    print("Data loaded")

t = threading.Thread(target=fetch_data, name="Worker1")
t.start()  # Initiates execution on OS thread
t.join()   # Main thread waits here until t terminates
```

### 4.2 Daemon Threads
- Standard (non-daemon) threads prevent the Python program from exiting until they finish.
- Set `daemon=True` for background services (metrics reporting, cache flushes). Daemon threads terminate immediately when the main thread exits.

### 4.3 The Global Interpreter Lock (GIL)
- The GIL is a mutual exclusion lock used by CPython to prevent multiple threads from executing Python bytecodes simultaneously.
- Because Python releases the GIL during blocking system calls (network I/O, sleep, disk access), multiple threads can wait for external I/O concurrently.
- For CPU-heavy math calculations, threads do not provide speedup; use **Multiprocessing** instead.

### 4.4 Race Conditions & Locks
When multiple threads read and write shared variables without coordination, operations can interleave unexpectedly.
A `threading.Lock` enforces mutual exclusion:
```python
lock = threading.Lock()

with lock:
    shared_counter += 1  # Atomic critical section
```

### 4.5 Semaphores and Events
- **`Semaphore(n)`**: Maintains an internal counter allowing at most `n` threads concurrent access to a resource pool (e.g. database connections).
- **`Event()`**: Thread coordination signal. Threads call `event.wait()` until another thread calls `event.set()`.

### 4.6 Thread-Safe Queues (`queue.Queue`)
`queue.Queue` provides thread-safe FIFO queuing with built-in locking. It is the gold standard for implementing Producer-Consumer architectures without writing manual lock handling.

### 4.7 Modern Thread Pools (`ThreadPoolExecutor`)
The `concurrent.futures` module provides a clean abstraction:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(download_func, url_list)
```

---

## 5. Frequently Asked Interview Questions

### Q1: What is the Python GIL and how does it impact multithreading?
**Answer**:
The Global Interpreter Lock (GIL) is a mechanism in CPython that ensures only one native thread executes Python bytecode at any given instant. While it limits CPU-bound parallel execution on multi-core systems, it allows true concurrency during I/O operations because CPython releases the GIL while waiting on network or disk sockets.

### Q2: What is the difference between `start()` and `run()` in `threading.Thread`?
**Answer**:
- `start()` spawns a new operating system thread and calls `run()` within that new thread.
- Calling `run()` directly executes the method synchronously in the **current** thread without spawning any new thread.

### Q3: When should you use `queue.Queue` instead of a plain Python `list`?
**Answer**:
A standard Python `list` is not thread-safe for compound operations (checking length + appending/popping). `queue.Queue` implements all required locking internally, providing thread-safe `put()`, `get()`, and blocking wait semantics.

---

## 6. How to Run

Run the script from your terminal:
```bash
python multithreading_concepts.py
```

---

## 7. Exercises

In [multithreading_concepts.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson13_Multithreading/multithreading_concepts.py):
1. **Parallel URL Checker**: Use `ThreadPoolExecutor` to query simulated server URLs concurrently.
2. **Thread-Safe Counter**: Build a class using `threading.Lock` to increment a shared counter across multiple threads without data races.
3. **Producer-Consumer Pipeline**: Connect a producer and multiple consumers using `queue.Queue` and a sentinel value.

---

## 8. Completion Checklist

- [ ] Run `python multithreading_concepts.py` and review output.
- [ ] Understand why the GIL affects CPU-bound vs. I/O-bound tasks differently.
- [ ] Complete exercise 1 (ThreadPoolExecutor).
- [ ] Complete exercise 2 (Thread-safe Lock counter).
- [ ] Complete exercise 3 (queue.Queue pipeline).
- [ ] Review all interview questions.
