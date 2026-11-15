"""
SYNOPSIS
    Lesson 15: Asynchronous Programming in Python (asyncio) -
    Event loop architecture, coroutines (async def / await), Task creation
    (asyncio.create_task), running concurrent tasks (asyncio.gather),
    timeouts (asyncio.timeout / wait_for), async iterators and context managers,
    asyncio.Queue, and bridging blocking code with asyncio.to_thread.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python asyncio_concepts.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import time
import asyncio

print("=" * 60)
print("LESSON 15: Asynchronous Programming in Python (asyncio)")
print("=" * 60)


# ============================================================
# 1. Coroutines: async def and await
# ============================================================
print("\n--- 1. Coroutines: async def & await ---")
# An `async def` function returns a coroutine object when called.
# It does NOT run immediately; it must be awaited or scheduled on the event loop.


async def fetch_user(user_id: int):
    print(f"  [fetch_user] Requesting profile for user {user_id}...")
    # asyncio.sleep is a non-blocking asynchronous sleep that yields control
    await asyncio.sleep(0.1)
    print(f"  [fetch_user] Received profile for user {user_id}.")
    return {"id": user_id, "username": f"user_{user_id}", "status": "active"}


async def demo_coroutine():
    user = await fetch_user(101)
    print(f"User retrieved: {user}")


# Entry point to the asyncio event loop
asyncio.run(demo_coroutine())


# ============================================================
# 2. Concurrent Execution: asyncio.create_task & asyncio.gather
# ============================================================
print("\n--- 2. Concurrent Tasks: asyncio.gather & create_task ---")


async def simulate_api_call(endpoint: str, delay: float) -> str:
    print(f"  --> Calling {endpoint} (est. {delay}s)...")
    await asyncio.sleep(delay)
    print(f"  <-- Received {endpoint}!")
    return f"Response from {endpoint}"


async def demo_gather():
    start = time.time()
    # asyncio.gather schedules all coroutines concurrently and waits for all of them
    results = await asyncio.gather(
        simulate_api_call("/api/users", 0.15),
        simulate_api_call("/api/orders", 0.20),
        simulate_api_call("/api/inventory", 0.10),
    )
    elapsed = time.time() - start
    print(f"All 3 endpoints resolved concurrently in {elapsed:.2f}s (sequential: ~0.45s)!")
    print(f"Results: {results}")


asyncio.run(demo_gather())


# ============================================================
# 3. Tasks & Background Execution: asyncio.create_task
# ============================================================
print("\n--- 3. Background Tasks with asyncio.create_task ---")


async def periodic_metric_logger():
    for count in range(3):
        await asyncio.sleep(0.05)
        print(f"  [Metric Logger] CPU load check #{count + 1} OK")


async def demo_tasks():
    # create_task wraps a coroutine into an independent Task and schedules it immediately
    background_task = asyncio.create_task(periodic_metric_logger())

    print("  [Main Task] Performing primary workflow...")
    await asyncio.sleep(0.18)
    print("  [Main Task] Primary workflow finished.")

    # Await task completion
    await background_task


asyncio.run(demo_tasks())


# ============================================================
# 4. Timeouts & Exception Handling
# ============================================================
print("\n--- 4. Timeouts & Exception Handling ---")


async def slow_database_query():
    await asyncio.sleep(0.5)
    return "Database Query Success"


async def demo_timeout():
    try:
        # Enforce a 0.1s timeout on a query that takes 0.5s
        await asyncio.wait_for(slow_database_query(), timeout=0.1)
    except asyncio.TimeoutError:
        print("Caught asyncio.TimeoutError: Operation exceeded deadline as expected!")


asyncio.run(demo_timeout())


# ============================================================
# 5. Async Iterators & Async Context Managers
# ============================================================
print("\n--- 5. Async Iterators & Async Context Managers ---")


class AsyncTicker:
    """Asynchronous iterator yielding ticks with non-blocking delays."""

    def __init__(self, count: int, delay: float):
        self.count = count
        self.delay = delay
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current < self.count:
            await asyncio.sleep(self.delay)
            self.current += 1
            return f"Tick #{self.current}"
        raise StopAsyncIteration


class AsyncConnection:
    """Asynchronous context manager using __aenter__ and __aexit__."""

    async def __aenter__(self):
        print("  [AsyncConnection] Opening async socket connection...")
        await asyncio.sleep(0.05)
        return self

    async def query(self, sql: str):
        return f"Result for '{sql}'"

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("  [AsyncConnection] Closing async socket connection...")
        await asyncio.sleep(0.02)


async def demo_async_protocols():
    print("Consuming AsyncTicker with 'async for':")
    async for tick in AsyncTicker(3, 0.03):
        print(f"  {tick}")

    print("Using AsyncConnection with 'async with':")
    async with AsyncConnection() as conn:
        res = await conn.query("SELECT * FROM users LIMIT 5")
        print(f"  Query result: {res}")


asyncio.run(demo_async_protocols())


# ============================================================
# 6. Async Producer-Consumer with asyncio.Queue
# ============================================================
print("\n--- 6. Async Producer-Consumer (asyncio.Queue) ---")


async def async_producer(q: asyncio.Queue):
    for item in ["Event-1", "Event-2", "Event-3"]:
        await q.put(item)
        print(f"  [Producer] Put {item}")
        await asyncio.sleep(0.03)
    await q.put(None)  # Sentinel to stop consumer


async def async_consumer(q: asyncio.Queue):
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            break
        print(f"  [Consumer] Processed {item}")
        q.task_done()


async def demo_queue():
    q = asyncio.Queue()
    await asyncio.gather(async_producer(q), async_consumer(q))


asyncio.run(demo_queue())


# ============================================================
# 7. Running Blocking Sync Code in asyncio: asyncio.to_thread
# ============================================================
print("\n--- 7. Bridging Blocking Code: asyncio.to_thread (Python 3.9+) ---")


def blocking_legacy_io(filename: str) -> str:
    """A standard synchronous blocking function (e.g. disk read or third-party SDK)."""
    time.sleep(0.1)  # Synchronous blocking sleep
    return f"Content of {filename}"


async def demo_to_thread():
    print("Delegating blocking sync call to thread pool without stalling the event loop...")
    # asyncio.to_thread runs the sync function on a separate worker thread
    content = await asyncio.to_thread(blocking_legacy_io, "report.pdf")
    print(f"Retrieved via asyncio.to_thread: '{content}'")


asyncio.run(demo_to_thread())


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python asyncio_concepts.py
# ============================================================
#
# 1. PARALLEL ASYNC FETCHER:
#    Write an async function `fetch_status(service_id)` that sleeps for 0.05s
#    and returns `f"Service {service_id}: HEALTHY"`.
#    Use `asyncio.gather()` to fetch statuses for services 1 through 5 concurrently.
#
# 2. TIMEOUT SHIELD:
#    Write an async function `simulated_download(delay)` that sleeps for `delay`.
#    Wrap a call to `simulated_download(0.5)` with `asyncio.wait_for(..., timeout=0.1)`.
#    Catch the `TimeoutError` and print `"Download timed out as expected"`.
#
# 3. ASYNC GENERATOR:
#    Create an async generator `async def count_down_async(start)` that yields numbers
#    down to 1, awaiting `asyncio.sleep(0.02)` between each yield.
#    Consume it using `async for`.

# --- write your code below this line ---
