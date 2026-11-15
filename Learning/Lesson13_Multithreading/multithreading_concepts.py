"""
SYNOPSIS
    Lesson 13: Multithreading in Python (threading & concurrent.futures) -
    Thread creation, threading.Thread, daemon threads, start() and join(),
    Global Interpreter Lock (GIL) mechanics, race conditions, thread synchronization
    primitives (threading.Lock, RLock, Semaphore, Event), thread-safe queues
    (queue.Queue), ThreadPoolExecutor, and I/O-bound workload benchmarking.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python multithreading_concepts.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 60)
print("LESSON 13: Multithreading in Python")
print("=" * 60)


# ============================================================
# 1. Basic Thread Creation, start(), and join()
# ============================================================
print("\n--- 1. Basic Thread Creation & join() ---")


def fetch_remote_resource(service_name: str, delay: float):
    """Simulates an I/O network call with a sleep delay."""
    print(f"  [{threading.current_thread().name}] Starting fetch for '{service_name}'...")
    time.sleep(delay)
    print(f"  [{threading.current_thread().name}] Finished fetch for '{service_name}'.")


start_time = time.time()
# Create threads
thread1 = threading.Thread(target=fetch_remote_resource, args=("Auth Service", 0.3), name="Worker-Auth")
thread2 = threading.Thread(target=fetch_remote_resource, args=("Payment API", 0.2), name="Worker-Payment")

# Start execution concurrently
thread1.start()
thread2.start()

# Wait for both threads to finish before proceeding
thread1.join()
thread2.join()

elapsed = time.time() - start_time
print(f"Both I/O calls completed concurrently in {elapsed:.2f}s (sequential would be ~0.50s)")


# ============================================================
# 2. Daemon vs Non-Daemon Threads
# ============================================================
print("\n--- 2. Daemon vs Non-Daemon Threads ---")
# Non-daemon threads keep the main Python process alive until they finish.
# Daemon threads run in the background and are automatically terminated when
# all non-daemon threads (including MainThread) terminate.


def background_heartbeat():
    for i in range(3):
        time.sleep(0.05)
        print(f"  [Heartbeat Daemon] Pulse {i + 1}")


heartbeat_thread = threading.Thread(target=background_heartbeat, daemon=True, name="HeartbeatDaemon")
heartbeat_thread.start()
print(f"Heartbeat thread is daemon: {heartbeat_thread.daemon}")
heartbeat_thread.join()  # Explicitly joining here so we see output in this script run


# ============================================================
# 3. The Global Interpreter Lock (GIL) & I/O vs CPU Bound
# ============================================================
print("\n--- 3. Python GIL: Why Threads excel at I/O but not CPU-bound tasks ---")
# The GIL is a mutex protecting access to Python objects, preventing multiple
# native threads from executing Python bytecode simultaneously on separate cores.
# - I/O-Bound (Disk/Network/Sleep): Python releases the GIL during blocking I/O,
#   allowing other threads to run concurrently. Excellent use of threading!
# - CPU-Bound (Heavy math/encoding): GIL prevents true multi-core parallel computation.
#   (Use multiprocessing for CPU-bound tasks instead).
print("  * Threads: Perfect for I/O-bound operations (Web requests, file reads, DB queries).")
print("  * GIL: Only ONE Python thread runs Python bytecode at any given instant per process.")


# ============================================================
# 4. Race Conditions & Synchronization with threading.Lock
# ============================================================
print("\n--- 4. Race Conditions & Thread Synchronization with Lock ---")


class BankBalance:
    def __init__(self, initial_balance: int = 0):
        self.balance = initial_balance
        self.lock = threading.Lock()

    def deposit_unsafe(self, amount: int):
        """Unsafe: non-atomic += can create race condition under heavy concurrency."""
        current = self.balance
        time.sleep(0.0001)  # Force OS context switch
        self.balance = current + amount

    def deposit_safe(self, amount: int):
        """Safe: acquired lock ensures mutual exclusion."""
        with self.lock:  # Automatically acquires and releases lock
            current = self.balance
            time.sleep(0.0001)
            self.balance = current + amount


safe_bank = BankBalance(0)
threads = []
for _ in range(10):
    t = threading.Thread(target=safe_bank.deposit_safe, args=(10,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Expected balance: 100 | Actual balance with Lock: {safe_bank.balance}")


# ============================================================
# 5. Advanced Primitives: Semaphore and Event
# ============================================================
print("\n--- 5. Advanced Synchronization: Semaphore and Event ---")

# Semaphore limits maximum concurrent access to a resource pool (e.g. max 2 DB connections)
db_semaphore = threading.Semaphore(2)


def access_database_pool(client_id: int):
    with db_semaphore:
        print(f"  [Client {client_id}] Acquired DB connection.")
        time.sleep(0.05)
        print(f"  [Client {client_id}] Released DB connection.")


sem_threads = [threading.Thread(target=access_database_pool, args=(i,)) for i in range(4)]
for t in sem_threads:
    t.start()
for t in sem_threads:
    t.join()

# Event: simple signaling mechanism between threads
ready_event = threading.Event()


def worker_waiting_for_signal():
    print("  [Worker] Waiting for readiness signal...")
    ready_event.wait()  # Blocks until ready_event.set() is called
    print("  [Worker] Signal received! Processing started.")


signal_worker = threading.Thread(target=worker_waiting_for_signal)
signal_worker.start()
time.sleep(0.1)
print("  [Main] Setting event flag now...")
ready_event.set()
signal_worker.join()


# ============================================================
# 6. Thread-Safe Communication with queue.Queue
# ============================================================
print("\n--- 6. Producer-Consumer Pattern with queue.Queue ---")
# queue.Queue handles internal locking automatically, making it completely thread-safe.

task_queue = queue.Queue(maxsize=5)


def producer():
    for item in ["DocA", "DocB", "DocC"]:
        task_queue.put(item)
        print(f"  [Producer] Pushed '{item}' to queue.")
        time.sleep(0.02)
    task_queue.put(None)  # Sentinel to signal termination


def consumer():
    while True:
        item = task_queue.get()
        if item is None:
            task_queue.task_done()
            break
        print(f"  [Consumer] Processed '{item}'.")
        task_queue.task_done()


prod_t = threading.Thread(target=producer)
cons_t = threading.Thread(target=consumer)
prod_t.start()
cons_t.start()
prod_t.join()
cons_t.join()


# ============================================================
# 7. Modern ThreadPoolExecutor (concurrent.futures)
# ============================================================
print("\n--- 7. Modern Thread Pools with ThreadPoolExecutor ---")


def download_site(site_url: str) -> dict:
    time.sleep(0.05)
    return {"url": site_url, "status": 200, "size_kb": 42}


urls = [
    "https://example.com/api/v1",
    "https://example.com/api/v2",
    "https://example.com/api/v3",
    "https://example.com/api/v4",
]

print("Dispatching downloads via ThreadPoolExecutor:")
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit tasks and collect future objects
    futures = [executor.submit(download_site, url) for url in urls]
    for future in as_completed(futures):
        result = future.result()
        print(f"  Downloaded: {result['url']} (Status: {result['status']})")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python multithreading_concepts.py
# ============================================================
#
# 1. PARALLEL URL CHECKER:
#    Given a list of simulated server URLs:
#    `servers = ["srv-us-east", "srv-eu-west", "srv-ap-south", "srv-sa-east"]`
#    Use `ThreadPoolExecutor` to query each server concurrently with a 0.05s
#    simulated delay and return the status: `f"{srv}: OK"`.
#
# 2. THREAD-SAFE COUNTER:
#    Implement a `Counter` class with an internal count and a `threading.Lock`.
#    Create 5 threads that each increment the counter 20 times. Ensure the final
#    count is exactly 100.
#
# 3. PRODUCER-CONSUMER WORKFLOW:
#    Create a `queue.Queue()`. Launch a producer thread that enqueues 5 order IDs
#    (e.g., 101 to 105), and two consumer threads that retrieve and process orders
#    until a sentinel `None` is encountered.

# --- write your code below this line ---
