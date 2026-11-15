"""
SYNOPSIS
    Lesson 10: Iterators and Generators - Iterable vs Iterator, iter(), next(),
    Iterator Protocol (__iter__, __next__), custom iterators, StopIteration,
    generators with yield, generator expressions, yield from, generator send(),
    lazy evaluation, memory efficiency comparison, and practical patterns.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python iterators_and_generators.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import sys
import time

print("=" * 60)
print("LESSON 10: Iterators and Generators")
print("=" * 60)


# ============================================================
# 1. Iterable vs Iterator & iter(), next()
# ============================================================
print("\n--- 1. Iterable vs Iterator & iter(), next() ---")

# An Iterable is any object that can return an iterator (implements __iter__ or __getitem__).
# Examples: list, tuple, str, dict, set.
# An Iterator is an object that represents a stream of data; it produces the next value
# via __next__() (or next()) and maintains internal state.

numbers = [10, 20, 30]
print(f"numbers (iterable): {numbers}, type: {type(numbers).__name__}")
print(f"Has __iter__: {'__iter__' in dir(numbers)}, Has __next__: {'__next__' in dir(numbers)}")

num_iter = iter(numbers)
print(f"num_iter (iterator): {num_iter}, type: {type(num_iter).__name__}")
print(f"Has __iter__: {'__iter__' in dir(num_iter)}, Has __next__: {'__next__' in dir(num_iter)}")

# Fetching elements one by one with next()
first = next(num_iter)
second = next(num_iter)
third = next(num_iter)
print(f"Fetched via next(): {first}, {second}, {third}")

# Providing a default value to next() avoids raising StopIteration
sentinel_val = next(num_iter, "END_OF_STREAM")
print(f"next(num_iter, default): {sentinel_val}")


# ============================================================
# 2. Iterator Protocol & StopIteration Under the Hood
# ============================================================
print("\n--- 2. Iterator Protocol & How 'for' Loops Work ---")

# Under the hood, Python's `for item in iterable:` does:
# 1. it = iter(iterable)
# 2. repeatedly calls item = next(it)
# 3. catches StopIteration exception and terminates cleanly.

sample_data = ["alpha", "beta", "gamma"]
manual_iter = iter(sample_data)

print("Manual loop using while + next() + StopIteration handling:")
while True:
    try:
        item = next(manual_iter)
        print(f"  Got item: {item}")
    except StopIteration:
        print("  Caught StopIteration -> iteration complete!")
        break


# ============================================================
# 3. Custom Iterators (Classes implementing __iter__ and __next__)
# ============================================================
print("\n--- 3. Custom Iterator Classes ---")


class CountUpTo:
    """A custom iterator that counts from 1 up to max_val."""

    def __init__(self, max_val: int):
        self.max_val = max_val
        self.current = 1

    def __iter__(self):
        # An iterator must return itself from __iter__()
        return self

    def __next__(self):
        if self.current <= self.max_val:
            val = self.current
            self.current += 1
            return val
        raise StopIteration


class FibonacciIterator:
    """Custom iterator generating n terms of the Fibonacci sequence."""

    def __init__(self, limit: int):
        self.limit = limit
        self.count = 0
        self.a = 0
        self.b = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.limit:
            raise StopIteration
        val = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return val


print("CountUpTo(5):", list(CountUpTo(5)))
print("FibonacciIterator(7):", [n for n in FibonacciIterator(7)])


# ============================================================
# 4. Generator Functions & the `yield` Keyword
# ============================================================
print("\n--- 4. Generator Functions & 'yield' ---")

# A generator function is defined like a normal function, but whenever it needs
# to generate a value, it uses the `yield` keyword instead of `return`.
# When called, it does NOT execute immediately; it returns a generator object.


def simple_number_stream():
    print("  [generator] Starting...")
    yield 100
    print("  [generator] Resuming after 1st yield...")
    yield 200
    print("  [generator] Resuming after 2nd yield...")
    yield 300
    print("  [generator] Done!")


gen = simple_number_stream()
print(f"Generator object: {gen}, type: {type(gen).__name__}")
print(f"1st call to next(): {next(gen)}")
print(f"2nd call to next(): {next(gen)}")
print(f"3rd call to next(): {next(gen)}")
try:
    next(gen)
except StopIteration:
    print("4th call raised StopIteration as expected.")


def fibonacci_gen(limit: int):
    """Generator function for Fibonacci numbers."""
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


print("Fibonacci from generator:", list(fibonacci_gen(8)))


# ============================================================
# 5. Generator Expressions
# ============================================================
print("\n--- 5. Generator Expressions ---")

# Generator expressions use parentheses `()` instead of brackets `[]`.
# They are evaluated lazily on-demand, consuming minimal memory.

list_comp = [x * x for x in range(5)]
gen_exp = (x * x for x in range(5))

print(f"List comprehension : {list_comp} (type: {type(list_comp).__name__})")
print(f"Generator expr    : {gen_exp} (type: {type(gen_exp).__name__})")
print(f"Values from gen   : {list(gen_exp)}")

# Direct argument passing without double parentheses:
sum_of_squares = sum(x * x for x in range(1, 6))
print(f"sum(x * x for x in range(1, 6)) = {sum_of_squares}")


# ============================================================
# 6. Delegating Iteration with `yield from`
# ============================================================
print("\n--- 6. Delegating Iteration with 'yield from' ---")

# `yield from <iterable>` delegates part of its operations to another generator or iterable.
# It cleanly flattens nested generators or sub-iterables and transparently handles
# bidirectional communication (send/throw/close/return value).


def chain_sequences(*iterables):
    """Yield items from multiple iterables sequentially using 'yield from'."""
    for it in iterables:
        yield from it


seq1 = [1, 2, 3]
seq2 = ("a", "b")
seq3 = {10, 20}
chained = list(chain_sequences(seq1, seq2, seq3))
print(f"Chained sequences: {chained}")


def flatten(nested_list):
    """Recursively flatten arbitrarily nested lists."""
    for item in nested_list:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


nested_data = [1, [2, [3, 4], 5], 6, [7, 8]]
print(f"Original nested data: {nested_data}")
print(f"Flattened: {list(flatten(nested_data))}")


# ============================================================
# 7. Advanced Generator Interaction: send(), close(), throw()
# ============================================================
print("\n--- 7. Generator Methods: send(), close(), throw() ---")

# Generators can also receive values via .send(value), acting as coroutines / data consumers.


def running_accumulator(initial: float = 0.0):
    """Coroutine that accumulates values sent to it via .send()."""
    total = initial
    while True:
        # yield total produces current sum, and pauses to receive next input
        increment = yield total
        if increment is not None:
            total += increment


acc = running_accumulator(10.0)
# Step 1: Prime the generator to advance it to the first yield
current_total = next(acc)  # or acc.send(None)
print(f"Accumulator primed. Initial total: {current_total}")

# Step 2: Send values to the generator
print(f"Sent 5.0 -> Running total: {acc.send(5.0)}")
print(f"Sent 15.5 -> Running total: {acc.send(15.5)}")
print(f"Sent -2.5 -> Running total: {acc.send(-2.5)}")

# Step 3: Close the generator
acc.close()
print("Accumulator closed successfully.")


# ============================================================
# 8. Lazy Evaluation & Memory Efficiency Comparison
# ============================================================
print("\n--- 8. Lazy Evaluation & Memory Efficiency ---")

n_elements = 1_000_000

# Compare memory usage between a complete list and a generator
list_data = [i for i in range(n_elements)]
gen_data = (i for i in range(n_elements))

list_size = sys.getsizeof(list_data)
gen_size = sys.getsizeof(gen_data)

print(f"Elements: {n_elements:,}")
print(f"List comprehension memory : {list_size:,} bytes ({list_size / (1024 * 1024):.2f} MB)")
print(f"Generator expression memory: {gen_size:,} bytes ({gen_size / 1024:.2f} KB)")
print(f"Memory reduction ratio   : {list_size / gen_size:,.1f}x less memory!")

# Clean up large list to free memory
del list_data


# ============================================================
# 9. Practical Examples: Streaming & Pipeline Processing
# ============================================================
print("\n--- 9. Practical Examples: Processing Pipeline ---")

# Simulated log line generator
raw_log_entries = [
    "2026-11-15 08:00:01 INFO Server started on port 8080",
    "2026-11-15 08:00:05 ERROR Database connection timeout to host db01",
    "2026-11-15 08:00:10 WARN High memory usage detected: 85%",
    "2026-11-15 08:00:15 ERROR Disk space below threshold: 5%",
    "2026-11-15 08:00:20 INFO Health check passed",
]


def log_stream(logs):
    """Simulates streaming log lines one by one."""
    for line in logs:
        yield line


def filter_errors(lines):
    """Pipeline stage: filter lines containing ERROR."""
    for line in lines:
        if "ERROR" in line:
            yield line


def format_error_alert(lines):
    """Pipeline stage: transform error lines into alert messages."""
    for line in lines:
        timestamp, _, message = line.partition(" ERROR ")
        yield f"[ALERT] At {timestamp.strip()}: {message.strip()}"


# Construct the pipeline (no processing occurs until consumed)
pipeline = format_error_alert(filter_errors(log_stream(raw_log_entries)))

print("Pipeline results:")
for alert in pipeline:
    print(f"  {alert}")


# Practical Example 2: Chunking stream of data
def chunk_stream(iterable, chunk_size: int):
    """Yield successive chunks of given size from iterable."""
    iterator = iter(iterable)
    while True:
        chunk = []
        for _ in range(chunk_size):
            try:
                chunk.append(next(iterator))
            except StopIteration:
                break
        if not chunk:
            break
        yield chunk


sample_items = list(range(1, 11))
print(f"Chunking {sample_items} into sizes of 3:")
for chunk in chunk_stream(sample_items, 3):
    print(f"  chunk: {chunk}")


# ============================================================
# 10. Common Pitfalls & Interview Questions Summary
# ============================================================
print("\n--- 10. Key Pitfalls & Takeaways ---")
print("1. Generators are ONE-TIME use (exhaustible). Once iterated, they are empty.")
one_time_gen = (x for x in [1, 2, 3])
print(f"   First pass : {list(one_time_gen)}")
print(f"   Second pass: {list(one_time_gen)} (empty!)")
print("2. Iterables can be iterated multiple times (like a list); iterators maintain state.")
print("3. Iterators define both __iter__() and __next__(); iterables need only __iter__().")
print("4. 'yield from' delegates to sub-generators cleanly and handles bidirectional data.")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python iterators_and_generators.py
# ============================================================
#
# 1. Implement a custom iterator class `EvenRange(start, stop)` that yields
#    all even numbers from `start` up to (and including, if even) `stop`.
#    Demonstrate it with `list(EvenRange(3, 11))` -> [4, 6, 8, 10].
#
# 2. Write a generator function `prime_generator(limit)` that yields prime
#    numbers up to `limit` using lazy evaluation.
#    Print all primes up to 30.
#
# 3. Create a generator expression that takes words from
#    `["python", "generator", "iterator", "stream", "yield"]`,
#    filters for words longer than 5 characters, and converts them to uppercase.
#    Iterate over the generator expression with a for loop.
#
# 4. Write a pipeline using two generator functions:
#    - `read_numbers(nums)`: yields numbers from a sequence
#    - `running_average(stream)`: accepts the stream and yields the running
#      cumulative average after each number.
#    Test it on `[10, 20, 30, 40]`, expecting outputs 10.0, 15.0, 20.0, 25.0.
#
# 5. Interview question test:
#    Explain why calling `iter()` on an iterator returns the iterator itself,
#    and demonstrate this behavior using `iter(gen)` and `id()`.

# --- write your code below this line ---
