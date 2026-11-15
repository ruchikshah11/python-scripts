"""
SYNOPSIS
    Lesson 14: Multiprocessing in Python (multiprocessing & ProcessPoolExecutor) -
    Bypassing the GIL for true parallel CPU execution, Process creation, start(),
    join(), Process pools (multiprocessing.Pool, map, starmap, apply_async),
    inter-process communication (IPC) via multiprocessing.Queue and Pipe,
    shared memory (Value, Array, Manager), CPU core count (os.cpu_count()),
    and CPU-bound performance benchmarking.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python multiprocessing_concepts.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import os
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor


# Top-level helper function for multiprocessing (must be pickleable)
def compute_square_heavy(n: int) -> int:
    """Simulates CPU-heavy mathematical computation."""
    total = 0
    for i in range(1, 100_000):
        total += (n * i) % 7
    return total


def worker_process_task(name: str, number: int, out_queue: mp.Queue):
    """Task executed in a dedicated process."""
    result = compute_square_heavy(number)
    out_queue.put((name, result, os.getpid()))


def increment_shared_value(shared_val, lock, iterations: int):
    """Safely increments a shared ctypes Value across processes."""
    for _ in range(iterations):
        with lock:
            shared_val.value += 1


def main():
    print("=" * 60)
    print("LESSON 14: Multiprocessing in Python")
    print("=" * 60)

    # ============================================================
    # 1. CPU Cores & Bypassing the GIL
    # ============================================================
    print("\n--- 1. CPU Cores & Process Isolation ---")
    core_count = os.cpu_count() or 1
    print(f"Available CPU logical cores: {core_count}")
    print(f"Main Process PID: {os.getpid()}")
    print("Multiprocessing bypasses the GIL by creating independent OS processes,")
    print("each with its own Python interpreter, memory space, and GIL instance.")

    # ============================================================
    # 2. Basic Process Creation, start(), and join()
    # ============================================================
    print("\n--- 2. Basic Process Creation with mp.Process ---")
    result_queue = mp.Queue()

    p1 = mp.Process(target=worker_process_task, args=("Proc-A", 15, result_queue))
    p2 = mp.Process(target=worker_process_task, args=("Proc-B", 25, result_queue))

    p1.start()
    p2.start()

    # Collect results from queue
    res1 = result_queue.get()
    res2 = result_queue.get()

    p1.join()
    p2.join()

    print(f"  Got from {res1[0]}: result={res1[1]}, PID={res1[2]}")
    print(f"  Got from {res2[0]}: result={res2[1]}, PID={res2[2]}")

    # ============================================================
    # 3. Process Pooling with multiprocessing.Pool
    # ============================================================
    print("\n--- 3. Process Pools (mp.Pool: map & apply_async) ---")
    data_items = [10, 20, 30, 40, 50, 60]

    with mp.Pool(processes=min(4, core_count)) as pool:
        # map() distributes tasks across worker pool and preserves order
        results = pool.map(compute_square_heavy, data_items)
        print(f"mp.Pool.map results for {data_items}:")
        print(f"  {results}")

        # apply_async() for non-blocking single task submission
        async_res = pool.apply_async(compute_square_heavy, (99,))
        print(f"mp.Pool.apply_async result for 99: {async_res.get(timeout=2)}")

    # ============================================================
    # 4. Inter-Process Communication (IPC): Pipe
    # ============================================================
    print("\n--- 4. Inter-Process Communication (IPC) via Pipe ---")
    # A Pipe returns two connection objects representing two ends of a duplex channel
    parent_conn, child_conn = mp.Pipe()

    def child_worker(conn):
        received_msg = conn.recv()
        response = f"Echo: '{received_msg}' processed by Child PID {os.getpid()}"
        conn.send(response)
        conn.close()

    pipe_proc = mp.Process(target=child_worker, args=(child_conn,))
    pipe_proc.start()

    parent_conn.send("Hello from Main Process!")
    reply = parent_conn.recv()
    print(f"Parent received: {reply}")
    pipe_proc.join()

    # ============================================================
    # 5. Shared Memory (Value, Array, Manager)
    # ============================================================
    print("\n--- 5. Shared State Across Process Memory Boundaries ---")
    # Because processes do not share memory, Python provides shared ctypes:
    shared_counter = mp.Value("i", 0)  # 'i' = signed integer
    shared_lock = mp.Lock()

    proc1 = mp.Process(target=increment_shared_value, args=(shared_counter, shared_lock, 50))
    proc2 = mp.Process(target=increment_shared_value, args=(shared_counter, shared_lock, 50))

    proc1.start()
    proc2.start()
    proc1.join()
    proc2.join()

    print(f"Expected count: 100 | Actual shared counter value: {shared_counter.value}")

    # Manager for complex shared structures (dicts, lists)
    with mp.Manager() as manager:
        shared_dict = manager.dict()
        shared_dict["status"] = "initialized"

        def update_dict(d, key, val):
            d[key] = val

        p = mp.Process(target=update_dict, args=(shared_dict, "worker_status", "completed"))
        p.start()
        p.join()
        print(f"Manager shared dict: {dict(shared_dict)}")

    # ============================================================
    # 6. ProcessPoolExecutor (concurrent.futures)
    # ============================================================
    print("\n--- 6. Modern ProcessPoolExecutor ---")
    numbers = [1, 2, 3, 4]
    with ProcessPoolExecutor(max_workers=min(4, core_count)) as executor:
        futures_results = list(executor.map(compute_square_heavy, numbers))
        print(f"ProcessPoolExecutor results: {futures_results}")

    # ============================================================
    # EXERCISE - write your code below this line, then run:
    #     python multiprocessing_concepts.py
    # ============================================================
    #
    # 1. PARALLEL FACTORIAL / POWER:
    #    Write a function `cpu_task(n)` that calculates `sum(x**2 for x in range(n))`.
    #    Use `ProcessPoolExecutor` to compute this for `[10_000, 20_000, 30_000, 40_000]`
    #    in parallel across available cores.
    #
    # 2. MULTIPROCESSING QUEUE:
    #    Launch 2 worker processes that compute cubes of numbers from a list
    #    and push tuples `(number, cube)` to an `mp.Queue`. The main process
    #    retrieves and prints all results.
    #
    # 3. SHARED VALUE SYNCHRONIZATION:
    #    Create an `mp.Value('d', 100.0)` representing a shared balance.
    #    Launch two processes: one withdraws 30.0, the other deposits 50.0.
    #    Use an `mp.Lock` to ensure synchronization and assert the final balance is 120.0.

    # --- write your code below this line ---


if __name__ == "__main__":
    # In multiprocessing (especially Windows and macOS spawn mode), code must be
    # protected by if __name__ == '__main__': to avoid infinite process spawning.
    main()
