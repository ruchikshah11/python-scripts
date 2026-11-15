"""
SYNOPSIS
    Lesson 18: Testing in Python (unittest and pytest) -
    Built-in unittest framework (TestCase, assertions, setUp/tearDown, setUpClass),
    pytest framework (test functions, plain assert, pytest fixtures with yield,
    parametrized tests with @pytest.mark.parametrize, exception testing with
    pytest.raises, test markers and filtering, and test discovery).

DESCRIPTION
    Run this file top-to-bottom to see unittest in action, or run it with
    `pytest test_learning.py` to see pytest discovery and execution.

EXAMPLE
    python test_learning.py
    pytest test_learning.py -v

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import unittest
import pytest

print("=" * 60)
print("LESSON 18: Testing in Python (unittest & pytest)")
print("=" * 60)


# ============================================================
# Core Business Logic to Test
# ============================================================
class BankAccount:
    """A simple bank account class for demonstrating unit tests."""

    def __init__(self, owner: str, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self.owner = owner
        self.balance = float(initial_balance)

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        return self.balance


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculates final price after applying discount percentage."""
    if not (0 <= discount_percent <= 100):
        raise ValueError("Discount percent must be between 0 and 100.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    return round(price * (1 - discount_percent / 100), 2)


# ============================================================
# PART 1: Standard Library unittest Framework
# ============================================================
# In unittest:
# 1. Test cases inherit from unittest.TestCase
# 2. Test methods must start with the prefix test_*
# 3. Use self.assertEqual, self.assertTrue, self.assertRaises, etc.
# 4. setUp() runs before EVERY test method; tearDown() runs after EVERY test method


class TestBankAccountUnittest(unittest.TestCase):
    """Demonstrates standard library unittest.TestCase features."""

    @classmethod
    def setUpClass(cls):
        """Runs once before any test in this class."""
        # E.g. connect to test database or initialize expensive fixtures
        cls.test_suite_name = "BankAccount Suite"

    def setUp(self):
        """Runs fresh before EACH test method to ensure test isolation."""
        self.account = BankAccount(owner="Navneet Saunee", initial_balance=100.0)

    def tearDown(self):
        """Runs cleanup after EACH test method."""
        pass

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.owner, "Navneet Saunee")

    def test_deposit_valid_amount(self):
        new_balance = self.account.deposit(50.0)
        self.assertEqual(new_balance, 150.0)
        self.assertEqual(self.account.balance, 150.0)

    def test_withdraw_valid_amount(self):
        new_balance = self.account.withdraw(40.0)
        self.assertEqual(new_balance, 60.0)

    def test_withdraw_insufficient_funds_raises_error(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(500.0)

    def test_negative_deposit_raises_error(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-10.0)


# ============================================================
# PART 2: Modern pytest Framework
# ============================================================
# Pytest advantages:
# 1. No classes or boilerplate inheritance required (simple functions).
# 2. Uses Python's native `assert` keyword with detailed failure introspection.
# 3. Powerful, reusable fixtures with `@pytest.fixture`.
# 4. Built-in parameterization with `@pytest.mark.parametrize`.
# 5. Exception assertion using `with pytest.raises(ExceptionType):`.


# --- Pytest Fixture ---
@pytest.fixture
def sample_account():
    """Provides a fresh BankAccount fixture for pytest tests.
    Code before yield is setup; code after yield is teardown.
    """
    account = BankAccount(owner="Navneet Saunee", initial_balance=200.0)
    yield account
    # Teardown / cleanup runs after test completes
    account.balance = 0.0


# --- Pytest Tests ---
def test_pytest_deposit(sample_account):
    """Test using plain assert with a fixture."""
    result = sample_account.deposit(100.0)
    assert result == 300.0
    assert sample_account.balance == 300.0


def test_pytest_withdraw_exception(sample_account):
    """Testing exceptions using pytest.raises with matching error text."""
    with pytest.raises(ValueError, match="Insufficient balance"):
        sample_account.withdraw(999.0)


# --- Pytest Parametrization ---
# Runs the test multiple times, once for each parameter tuple
@pytest.mark.parametrize(
    "price,discount,expected",
    [
        (100.0, 10, 90.0),    # 10% off 100
        (50.0, 50, 25.0),     # 50% off 50
        (200.0, 0, 200.0),    # 0% off 200
        (80.0, 100, 0.0),     # 100% off 80
        (99.99, 15, 84.99),   # Rounded discount
    ],
)
def test_pytest_calculate_discount_parametrized(price, discount, expected):
    """Parametrized test running 5 scenarios cleanly."""
    assert calculate_discount(price, discount) == expected


def test_invalid_discount_raises():
    with pytest.raises(ValueError, match="between 0 and 100"):
        calculate_discount(100.0, 150)


# ============================================================
# EXERCISE - write your tests below this line:
# ============================================================
#
# 1. UNITTEST TESTCASE:
#    Create a function `format_full_name(first, last)` that returns `f"{last}, {first}"`.
#    Write a `unittest.TestCase` class named `TestNameFormatter` testing:
#      - Standard input `format_full_name("Navneet", "Saunee")` == `"Saunee, Navneet"`
#      - Empty string inputs raise ValueError
#
# 2. PYTEST PARAMETRIZATION:
#    Write a function `is_palindrome(text: str) -> bool`.
#    Write a `@pytest.mark.parametrize` test function checking 4 palindromes
#    ("racecar", "madam", "noon", "radar") and 2 non-palindromes.
#
# 3. PYTEST FIXTURE TEARDOWN:
#    Create a fixture `temporary_log_file` that creates a file, yields its Path,
#    and deletes it during teardown.


if __name__ == "__main__":
    # When run directly with `python test_learning.py`, execute unittest suite
    print("\nRunning unittest test suite...")
    unittest.main(verbosity=2)
