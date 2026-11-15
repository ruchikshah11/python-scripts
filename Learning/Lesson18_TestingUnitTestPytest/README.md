# Lesson 18: Testing in Python (`unittest` and `pytest`)

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable test suite covering software testing in Python. Learn both Python's built-in `unittest` standard library and the industry-standard `pytest` framework, covering test cases, assertions, setup/teardown fixtures, test parameterization, and exception testing.

---

## 1. Introduction

Automated testing ensures that code behaves as expected, catches regressions before deployment, and facilitates confident refactoring.

In Python, two frameworks dominate the ecosystem:
1. **`unittest`**: The standard library testing framework modeled after Java's JUnit. It uses an object-oriented approach with test classes and explicit assert methods (`self.assertEqual`, `self.assertRaises`).
2. **`pytest`**: The industry-standard third-party framework known for minimal boilerplate, standalone test functions, native Python `assert` statements, powerful fixtures, and parameterized tests.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Write structured test suites using the built-in `unittest.TestCase`.
2. Manage test lifecycles with `setUp()`, `tearDown()`, and `setUpClass()`.
3. Write clean, idiomatic tests with `pytest` using plain `assert` statements.
4. Implement reusable setup and teardown logic using `@pytest.fixture` and `yield`.
5. Run dozens of test permutations effortlessly with `@pytest.mark.parametrize`.
6. Assert expected exceptions using `with self.assertRaises(...)` and `with pytest.raises(...)`.
7. Execute and filter tests using the CLI (`pytest -v`, `pytest -k`, `python -m unittest`).
8. Compare `unittest` vs. `pytest` to make informed architectural decisions.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. `unittest` vs. `pytest` Feature Comparison](#4-unittest-vs-pytest-feature-comparison)
- [5. The `unittest` Framework](#5-the-unittest-framework)
  - [5.1 TestCase and Test Discovery](#51-testcase-and-test-discovery)
  - [5.2 Assert Methods](#52-assert-methods)
  - [5.3 Setup and Teardown Lifecycle](#53-setup-and-teardown-lifecycle)
- [6. The `pytest` Framework](#6-the-pytest-framework)
  - [6.1 Native `assert` Introspection](#61-native-assert-introspection)
  - [6.2 Fixtures & Dependency Injection](#62-fixtures--dependency-injection)
  - [6.3 Parametrization (`@pytest.mark.parametrize`)](#63-parametrization-pytestmarkparametrize)
  - [6.4 Testing Exceptions (`pytest.raises`)](#64-testing-exceptions-pytestraises)
- [7. Frequently Asked Interview Questions](#7-frequently-asked-interview-questions)
- [8. How to Run](#8-how-to-run)
- [9. Exercises](#9-exercises)
- [10. Completion Checklist](#10-completion-checklist)

---

## 4. `unittest` vs. `pytest` Feature Comparison

| Feature | `unittest` (Standard Library) | `pytest` (Third-Party / Industry Standard) |
| :--- | :--- | :--- |
| **Installation** | Built-in (no installation) | `pip install pytest` |
| **Test Structure** | Classes inheriting `unittest.TestCase` | Simple functions or classes (no inheritance) |
| **Assertion Syntax** | `self.assertEqual(a, b)` | Plain `assert a == b` |
| **Fixtures** | `setUp()` / `tearDown()` methods | Reusable `@pytest.fixture` dependency injection |
| **Parametrization** | Subtests or loops | Clean `@pytest.mark.parametrize` decorator |
| **CLI Runner** | `python -m unittest` | `pytest` (runs both pytest and unittest tests!) |

---

## 5. The `unittest` Framework

```python
import unittest

class TestMath(unittest.TestCase):
    def setUp(self):
        # Runs before every test method
        self.data = [1, 2, 3]

    def test_sum(self):
        self.assertEqual(sum(self.data), 6)

    def test_zero_division(self):
        with self.assertRaises(ZeroDivisionError):
            _ = 1 / 0
```

---

## 6. The `pytest` Framework

### 6.1 Native `assert` Introspection
Pytest rewrites Python's `assert` statements during test execution, providing rich failure diagnostics showing exact intermediate values without needing dedicated helper methods:
```python
def test_plain_assert():
    result = calculate_discount(100, 20)
    assert result == 80.0
```

### 6.2 Fixtures & Dependency Injection
```python
import pytest

@pytest.fixture
def temp_account():
    # Setup
    acc = BankAccount("Navneet", 100)
    yield acc
    # Teardown
    acc.balance = 0
```

### 6.3 Parametrization (`@pytest.mark.parametrize`)
```python
@pytest.mark.parametrize("price,discount,expected", [
    (100, 10, 90),
    (50, 50, 25),
    (200, 0, 200),
])
def test_discount(price, discount, expected):
    assert calculate_discount(price, discount) == expected
```

### 6.4 Testing Exceptions (`pytest.raises`)
```python
def test_invalid_input():
    with pytest.raises(ValueError, match="cannot be negative"):
        BankAccount("Navneet", -50)
```

---

## 7. Frequently Asked Interview Questions

### Q1: Why does pytest recognize and run `unittest.TestCase` classes automatically?
**Answer**:
Pytest is designed to be fully backward-compatible. Its test runner discovers all files named `test_*.py` or `*_test.py` and runs both standalone `test_*` functions and classes derived from `unittest.TestCase`.

### Q2: How does fixture scope work in pytest?
**Answer**:
Fixtures can be configured with different lifecycles via the `scope` parameter:
- `function` (default): Created and torn down for each individual test function.
- `class`: Shared once across all test methods in a class.
- `module`: Shared once across all tests within a module/file.
- `session`: Shared once across the entire test run (ideal for expensive resources like Docker containers or test databases).

### Q3: What is the benefit of pytest's `yield` in fixtures over `tearDown()`?
**Answer**:
In pytest, placing code after `yield` within a fixture keeps setup and teardown logic colocated in a single function, preserving local variables naturally without needing to attach them to `self` as class attributes.

---

## 8. How to Run

### Run using Python's built-in `unittest`:
```bash
python test_learning.py
```

### Run using `pytest` (detailed output):
```bash
pytest test_learning.py -v
```

---

## 9. Exercises

In [test_learning.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson18_TestingUnitTestPytest/test_learning.py):
1. **Unittest TestCase**: Implement `TestNameFormatter` testing valid input and exception handling.
2. **Pytest Parametrization**: Test `is_palindrome()` across 6 varied test strings using `@pytest.mark.parametrize`.
3. **Fixture with Teardown**: Build a `temporary_log_file` fixture that automatically removes the created file after test execution.

---

## 10. Completion Checklist

- [ ] Run `python test_learning.py` using `unittest`.
- [ ] Run `pytest test_learning.py -v` using `pytest`.
- [ ] Complete exercise 1 (unittest TestCase).
- [ ] Complete exercise 2 (pytest parametrize).
- [ ] Complete exercise 3 (pytest fixture with yield).
- [ ] Review all interview questions and the comparison table.
