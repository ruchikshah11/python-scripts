# Lesson 14: Multiprocessing in Python (`multiprocessing` & `ProcessPoolExecutor`)

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering true multi-core parallel programming in Python using the `multiprocessing` module and `concurrent.futures.ProcessPoolExecutor`. Learn how multiprocessing bypasses the Python Global Interpreter Lock (GIL), handles Inter-Process Communication (IPC with `Queue` and `Pipe`), shares memory safely (`Value`, `Array`, `Manager`), and achieves maximum throughput on CPU-bound workloads.

---

## 1. Introduction

Unlike threads which share the same memory space and are restricted by CPython's Global Interpreter Lock (GIL) to a single core, **multiprocessing** spawns separate operating system processes.

Each process has:
- Its own private address space and memory
- Its own Python interpreter
- Its own independent GIL

This architecture enables Python programs to achieve **true CPU parallelism**, taking full advantage of modern multi-core processors.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain how **multiprocessing** bypasses the GIL to unlock multi-core CPU parallelism.
2. Spawn and manage processes with `multiprocessing.Process`, `.start()`, and `.join()`.
3. Understand the necessity of `if __name__ == '__main__':` on all platforms.
4. Distribute batch computations across worker pools using `multiprocessing.Pool` (`map`, `starmap`, `apply_async`).
5. Transmit data between processes using **Inter-Process Communication (IPC)** via `Queue` and `Pipe`.
6. Share state across memory boundaries using `Value`, `Array`, and `Manager`.
7. Utilize `concurrent.futures.ProcessPoolExecutor` for modern, clean task pooling.
8. Answer technical interview questions comparing multiprocessing vs. multithreading.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Core Multiprocessing Concepts](#4-core-multiprocessing-concepts)
  - [4.1 Why Multiprocessing Bypasses the GIL](#41-why-multiprocessing-bypasses-the-gil)
  - [4.2 The `if __name__ == '__main__':` Requirement](#42-the-if-__name__--__main__-requirement)
  - [4.3 Spawning Processes](#43-spawning-processes)
  - [4.4 Process Pools (`multiprocessing.Pool`)](#44-process-pools-multiprocessingpool)
  - [4.5 Inter-Process Communication (Queue & Pipe)](#45-inter-process-communication-queue--pipe)
  - [4.6 Shared Memory & Synchronization](#46-shared-memory--synchronization)
  - [4.7 Modern Task Pools (`ProcessPoolExecutor`)](#47-modern-task-pools-processpoolexecutor)
- [5. Multithreading vs. Multiprocessing Comparison](#5-multithreading-vs-multiprocessing-comparison)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. Core Multiprocessing Concepts

### 4.1 Why Multiprocessing Bypasses the GIL
Because each child process has its own dedicated Python interpreter and memory space, each has its own GIL. None of the processes block each other, enabling 100% CPU utilization across all available cores.

### 4.2 The `if __name__ == '__main__':` Requirement
When child processes are spawned (especially on Windows or macOS using the `spawn` start method), the new process imports the main script file. Wrapping process launching in `if __name__ == '__main__':` prevents an infinite recursive loop of child processes creating more child processes.

### 4.3 Spawning Processes
```python
import multiprocessing as mp

def worker(num):
    print(f"Worker {num}")

if __name__ == '__main__':
    p = mp.Process(target=worker, args=(1,))
    p.start()
    p.join()
```

### 4.4 Process Pools (`multiprocessing.Pool`)
```python
with mp.Pool(processes=4) as pool:
    results = pool.map(compute_heavy_math, [1, 2, 3, 4, 5])
```

### 4.5 Inter-Process Communication (Queue & Pipe)
- **`mp.Queue`**: Multi-producer, multi-consumer FIFO queue that safely serializes objects across process boundaries via `pickle`.
- **`mp.Pipe`**: Direct duplex (two-way) connection between two processes (`parent_conn.send()` / `child_conn.recv()`).

### 4.6 Shared Memory & Synchronization
- **`mp.Value` / `mp.Array`**: Low-level ctypes memory blocks shared between processes (synchronized via `mp.Lock`).
- **`mp.Manager`**: Server process managing proxy objects for high-level structures like dictionaries and lists.

### 4.7 Modern Task Pools (`ProcessPoolExecutor`)
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(my_cpu_func, [10, 20, 30]))
```

---

## 5. Multithreading vs. Multiprocessing Comparison

| Feature | Multithreading (`threading`) | Multiprocessing (`multiprocessing`) |
| :--- | :--- | :--- |
| **Execution Model** | Multiple threads inside 1 process | Multiple OS processes |
| **Memory Space** | Shared memory (fast, risk of race conditions) | Isolated memory (safe, requires IPC) |
| **GIL Bound?** | Yes (1 thread runs Python code at a time) | No (each process has its own GIL) |
| **Best Workload** | **I/O-Bound** (APIs, network, files) | **CPU-Bound** (heavy math, data crunching) |
| **Overhead** | Lightweight creation & memory footprint | Higher memory footprint & process startup |

---

## 6. Frequently Asked Interview Questions

### Q1: What is the key difference between multithreading and multiprocessing in Python?
**Answer**:
Multithreading runs within a single memory space and is constrained by CPython's GIL, making it effective primarily for I/O-bound tasks. Multiprocessing launches separate processes with isolated memory spaces and separate GIL instances, achieving true multi-core parallel computation on CPU-bound workloads.

### Q2: Why must target functions passed to worker processes be pickleable?
**Answer**:
Because processes do not share memory, all arguments, function references, and return values must be serialized into bytes (pickled) by the main process and transmitted over IPC channels (sockets/pipes) to the child process.

### Q3: Why is `if __name__ == '__main__':` required in multiprocessing?
**Answer**:
On operating systems using `spawn` (Windows, macOS, and Linux non-fork), each new process starts by re-importing the script. Without the `__name__ == '__main__'` guard, the child process would execute the process-creation code again, resulting in a recursive fork-bomb crash (`RuntimeError`).

---

## 7. How to Run

Run the script from your terminal:
```bash
python multiprocessing_concepts.py
```

---

## 8. Exercises

In [multiprocessing_concepts.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson14_Multiprocessing/multiprocessing_concepts.py):
1. **Parallel Math Calculation**: Use `ProcessPoolExecutor` to compute sum of squares across multiple integer inputs.
2. **IPC Queue Communication**: Distribute items from a list across 2 processes using `mp.Queue`.
3. **Synchronized Shared Memory**: Use `mp.Value` and `mp.Lock` to coordinate deposits and withdrawals across two separate processes.

---

## 9. Completion Checklist

- [ ] Run `python multiprocessing_concepts.py` and inspect all results.
- [ ] Understand why multiprocessing bypasses the GIL.
- [ ] Complete exercise 1 (ProcessPoolExecutor).
- [ ] Complete exercise 2 (mp.Queue).
- [ ] Complete exercise 3 (mp.Value & mp.Lock).
- [ ] Review all interview questions.
