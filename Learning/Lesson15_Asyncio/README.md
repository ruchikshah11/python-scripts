# Lesson 15: Asynchronous Programming in Python (`asyncio`)

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering asynchronous programming in Python with the `asyncio` standard library. Master the single-threaded event loop architecture, coroutines (`async def` and `await`), concurrent scheduling (`asyncio.gather`, `asyncio.create_task`), timeouts (`wait_for`), asynchronous iterators and context managers (`async for`, `async with`), asynchronous producer-consumer queues (`asyncio.Queue`), and bridging legacy blocking code (`asyncio.to_thread`).

---

## 1. Introduction

`asyncio` is Python's built-in framework for writing **single-threaded concurrent code** using coroutines, multiplexing I/O access over an **Event Loop**.

### Why `asyncio`?
- **Extreme Concurrency**: Can handle tens of thousands of simultaneous network connections (websockets, microservices, chat apps) with minimal memory overhead, unlike OS threads where each thread consumes 1–8 MB of stack memory.
- **Cooperative Multitasking**: Context switching happens explicitly at defined `await` points, eliminating race conditions on shared memory without requiring complex mutex locks.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain the **Event Loop** architecture and cooperative multitasking.
2. Define and await coroutines using `async def` and `await`.
3. Schedule concurrent coroutines using `asyncio.gather()` and background `asyncio.create_task()`.
4. Apply execution deadlines and handle timeouts with `asyncio.wait_for()`.
5. Implement asynchronous iterators (`__aiter__`, `__anext__`) and consume them via `async for`.
6. Implement asynchronous context managers (`__aenter__`, `__aexit__`) with `async with`.
7. Coordinate async tasks using `asyncio.Queue`.
8. Safely bridge synchronous blocking code using `asyncio.to_thread()`.
9. Choose accurately between **Multithreading**, **Multiprocessing**, and **Asyncio**.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Asyncio Mechanics](#4-core-asyncio-mechanics)
  - [4.1 Coroutines and `await`](#41-coroutines-and-await)
  - [4.2 The Event Loop & `asyncio.run()`](#42-the-event-loop--asynciorun)
  - [4.3 Concurrent Execution: `gather` vs `create_task`](#43-concurrent-execution-gather-vs-createtask)
  - [4.4 Timeouts & Deadlines](#44-timeouts--deadlines)
  - [4.5 Async Protocols (`async for` & `async with`)](#45-async-protocols-async-for--async-with)
  - [4.6 Async Producer-Consumer (`asyncio.Queue`)](#46-async-producer-consumer-asyncioqueue)
  - [4.7 Running Blocking Code (`asyncio.to_thread`)](#47-running-blocking-code-asynciotothread)
- [5. Concurrency Decision Matrix (Threads vs. Processes vs. Asyncio)](#5-concurrency-decision-matrix-threads-vs-processes-vs-asyncio)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. Core Asyncio Mechanics

### 4.1 Coroutines and `await`
- Calling an `async def` function returns a **coroutine object** without executing its body.
- Using `await coroutine` pauses the calling coroutine and yields control back to the event loop until the awaited operation produces a result.

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # Non-blocking pause
    return "Data ready"

# Run top-level coroutine
result = asyncio.run(fetch_data())
```

### 4.2 The Event Loop & `asyncio.run()`
The event loop acts as the central scheduler:
1. It tracks all pending tasks and I/O callbacks.
2. When a coroutine awaits an I/O operation, the loop switches execution to another ready task.
3. `asyncio.run(main())` creates a new event loop, executes the passed coroutine, and closes the loop automatically.

### 4.3 Concurrent Execution: `gather` vs `create_task`
- **`asyncio.gather(*coros)`**: Awaits a collection of coroutines concurrently and returns their aggregated results in order.
- **`asyncio.create_task(coro)`**: Immediately wraps a coroutine in an independent `Task` object, scheduling it on the event loop in the background.

### 4.4 Timeouts & Deadlines
```python
try:
    result = await asyncio.wait_for(fetch_data(), timeout=2.0)
except asyncio.TimeoutError:
    print("Operation timed out!")
```

### 4.5 Async Protocols (`async for` & `async with`)
- **`async with`**: Calls `await obj.__aenter__()` upon entry and `await obj.__aexit__()` upon exit.
- **`async for`**: Repeatedly calls `await obj.__anext__()` until `StopAsyncIteration` is raised.

### 4.6 Async Producer-Consumer (`asyncio.Queue`)
`asyncio.Queue` provides non-blocking FIFO queuing:
```python
q = asyncio.Queue(maxsize=10)
await q.put(item)     # Suspends if queue is full
item = await q.get()  # Suspends if queue is empty
```

### 4.7 Running Blocking Code (`asyncio.to_thread`)
In Python 3.9+, never run standard blocking operations (`time.sleep`, synchronous requests, heavy disk reads) directly on the event loop. Delegate them to a worker thread:
```python
result = await asyncio.to_thread(legacy_blocking_function, arg1)
```

---

## 5. Concurrency Decision Matrix

| Dimension | Multithreading (Lesson 13) | Multiprocessing (Lesson 14) | Asyncio (Lesson 15) |
| :--- | :--- | :--- | :--- |
| **Paradigm** | Preemptive multitasking | Preemptive multi-process | Cooperative multitasking |
| **Execution** | Multi-threaded (1 core at a time for Python) | True multi-core parallel | Single thread, 1 core |
| **GIL Bound?** | Yes | No (each process has its own GIL) | Yes (single thread) |
| **Memory** | Shared memory | Isolated per process | Shared single-thread heap |
| **Best For** | I/O-bound (disk, DB, small thread counts) | **CPU-bound** (math, video, ML, crunching) | **Massive I/O concurrency** (10,000+ sockets, APIs) |
| **Overhead** | Medium (~MBs per thread) | High (process spawn & IPC) | Very low (~hundreds of bytes per task) |

---

## 6. Frequently Asked Interview Questions

### Q1: What happens if you call `time.sleep()` inside an `async def` function?
**Answer**:
`time.sleep()` is a synchronous, blocking system call. It blocks the **entire OS thread**, freezing the event loop completely so that no other coroutines or tasks can execute during that interval. In async code, always use non-blocking `await asyncio.sleep()` or delegate synchronous blocking code via `await asyncio.to_thread()`.

### Q2: What is the difference between `asyncio.gather()` and `asyncio.wait()`?
**Answer**:
- `asyncio.gather()` takes multiple awaitables, runs them concurrently, and returns a list of results in the order they were submitted.
- `asyncio.wait()` accepts an iterable of Tasks and provides granular completion control (e.g., `return_when=asyncio.FIRST_COMPLETED`), returning sets of `(done, pending)` tasks.

### Q3: Why is `asyncio` able to handle thousands of concurrent connections while threads struggle?
**Answer**:
Threads require the operating system to allocate a separate stack (typically 1–8 MB per thread) and perform kernel-level context switches. `asyncio` tasks are lightweight Python coroutine objects with virtually zero stack overhead, scheduled via user-space event loops (using OS primitives like `epoll` / `kqueue`).

---

## 7. How to Run

Run the script from your terminal:
```bash
python asyncio_concepts.py
```

---

## 8. Exercises

In [asyncio_concepts.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson15_Asyncio/asyncio_concepts.py):
1. **Parallel Async Fetcher**: Write an async function that sleeps for 0.05s and use `asyncio.gather()` to fetch 5 statuses concurrently.
2. **Timeout Shield**: Enforce an `asyncio.wait_for` timeout of 0.1s on a slow task and cleanly catch `TimeoutError`.
3. **Async Generator**: Implement `async def count_down_async(start)` with `await asyncio.sleep()` and consume it with `async for`.

---

## 9. Completion Checklist

- [ ] Run `python asyncio_concepts.py` and inspect all outputs.
- [ ] Understand the event loop and cooperative multitasking.
- [ ] Complete exercise 1 (asyncio.gather).
- [ ] Complete exercise 2 (Timeout handling).
- [ ] Complete exercise 3 (Async generator).
- [ ] Review all interview questions and the Concurrency Decision Matrix.
