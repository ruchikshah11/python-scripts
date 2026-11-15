"""
SYNOPSIS
    Lesson 11: Object-Oriented Programming (OOP) in Python - The 4 Core Pillars:
    Encapsulation, Abstraction, Inheritance, and Polymorphism, plus Classes,
    Objects, __init__, self, Class vs Instance attributes, Methods (instance,
    @classmethod, @staticmethod), Properties (@property, getters/setters),
    Multiple Inheritance & MRO, and Abstract Base Classes (abc.ABC, @abstractmethod).

DESCRIPTION
    Run this file top-to-bottom to see each concept's output, then complete
    the exercises at the bottom.

EXAMPLE
    python oop_concepts.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

from abc import ABC, abstractmethod

print("=" * 60)
print("LESSON 11: Object-Oriented Programming (OOP) in Python")
print("=" * 60)


# ============================================================
# 1. Classes, Objects, __init__, and self
# ============================================================
print("\n--- 1. Classes, Objects, __init__, and self ---")


class Developer:
    """Represents a software developer profile."""

    # Class attribute (shared across all instances)
    role_domain = "Software Engineering"

    def __init__(self, name: str, level: str, experience_years: int):
        # Instance attributes (unique to each instance)
        self.name = name
        self.level = level
        self.experience_years = experience_years

    def introduce(self) -> str:
        """Instance method: operates on instance data through self."""
        return (
            f"Hi, I am {self.name}, a {self.level} engineer "
            f"with {self.experience_years} years in {self.role_domain}."
        )


dev1 = Developer("Navneet Saunee", "Lead", 8)
dev2 = Developer("Alex", "Junior", 1)

print(dev1.introduce())
print(dev2.introduce())
print(f"dev1 class domain: {dev1.role_domain}")
print(f"Are dev1 and dev2 classes identical? {dev1.__class__ is dev2.__class__}")


# ============================================================
# 2. Methods: Instance, @classmethod, and @staticmethod
# ============================================================
print("\n--- 2. Instance Methods, Class Methods, and Static Methods ---")


class Employee:
    base_annual_bonus_rate = 0.10  # 10%

    def __init__(self, emp_id: str, name: str, salary: float):
        self.emp_id = emp_id
        self.name = name
        self.salary = salary

    # 1. Instance method: receives instance as first argument (self)
    def calculate_bonus(self) -> float:
        return self.salary * self.base_annual_bonus_rate

    # 2. Class method: receives class as first argument (cls), useful as alternative constructors
    @classmethod
    def from_string(cls, emp_string: str):
        """Alternative constructor parsing 'ID,Name,Salary'."""
        emp_id, name, salary_str = emp_string.split(",")
        return cls(emp_id.strip(), name.strip(), float(salary_str.strip()))

    @classmethod
    def set_bonus_rate(cls, new_rate: float):
        cls.base_annual_bonus_rate = new_rate

    # 3. Static method: does not receive self or cls, acts like an isolated utility function
    @staticmethod
    def is_valid_emp_id(emp_id: str) -> bool:
        return emp_id.startswith("EMP-") and len(emp_id) == 8


# Using alternative constructor
emp1 = Employee.from_string("EMP-1001, Navneet Saunee, 120000")
print(f"Created from string: {emp1.name} (ID: {emp1.emp_id}), Salary: ${emp1.salary:,.2f}")
print(f"Calculated bonus: ${emp1.calculate_bonus():,.2f}")

# Calling static utility method
print(f"Is 'EMP-1001' valid? {Employee.is_valid_emp_id('EMP-1001')}")
print(f"Is 'BAD-99' valid? {Employee.is_valid_emp_id('BAD-99')}")


# ============================================================
# 3. PILLAR 1: ENCAPSULATION & DATA HIDING
# ============================================================
print("\n--- 3. Pillar 1: Encapsulation (Public, Protected, Private, @property) ---")

# Python naming conventions:
#   public_var: accessible everywhere
#   _protected_var: internal use convention (not enforced by interpreter)
#   __private_var: name-mangled to _ClassName__private_var to prevent accidental override


class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0.0):
        self.owner = owner          # Public attribute
        self._account_type = "Savings"  # Protected convention
        self.__balance = initial_balance  # Private attribute (name mangling)

    # Getter property
    @property
    def balance(self) -> float:
        """Read-only property access to the private balance."""
        return self.__balance

    # Deposit method (controlled state modification)
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount
        print(f"Deposited ${amount:,.2f}. New balance: ${self.__balance:,.2f}")

    # Withdraw method
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.__balance:
            raise ValueError(f"Insufficient funds: available ${self.__balance:,.2f}")
        self.__balance -= amount
        print(f"Withdrew ${amount:,.2f}. New balance: ${self.__balance:,.2f}")


account = BankAccount("Navneet Saunee", 5000.0)
print(f"Owner: {account.owner}, Balance via property: ${account.balance:,.2f}")
account.deposit(1500.0)
account.withdraw(2000.0)

# Demonstrating name mangling:
try:
    print(account.__balance)
except AttributeError:
    print("Direct access account.__balance raised AttributeError (Private & Protected!)")

# Name-mangled attribute exists under _BankAccount__balance:
print(f"Mangled access (_BankAccount__balance): ${account._BankAccount__balance:,.2f}")


# ============================================================
# 4. PILLAR 2: ABSTRACTION (ABC & @abstractmethod)
# ============================================================
print("\n--- 4. Pillar 2: Abstraction (Abstract Base Classes) ---")

# Abstraction hides complex implementation details and exposes only an essential interface.
# Classes inheriting from ABC with @abstractmethod CANNOT be instantiated directly.


class NotificationService(ABC):
    """Abstract interface for notification dispatchers."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the service."""
        pass

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Send message to recipient."""
        pass

    # Concrete method shared by all subclasses
    def log_notification(self, recipient: str):
        print(f"[AUDIT LOG] Notification dispatched to {recipient}")


class EmailNotification(NotificationService):
    def connect(self) -> None:
        print("Connected to SMTP email server.")

    def send(self, recipient: str, message: str) -> bool:
        print(f"Sending Email to <{recipient}>: '{message}'")
        self.log_notification(recipient)
        return True


class SMSNotification(NotificationService):
    def connect(self) -> None:
        print("Connected to SMS cellular gateway.")

    def send(self, recipient: str, message: str) -> bool:
        print(f"Sending SMS to {recipient}: '{message}'")
        self.log_notification(recipient)
        return True


# Attempting to instantiate the abstract class directly fails:
try:
    NotificationService()
except TypeError as err:
    print(f"Cannot instantiate abstract class: {err}")

# Instantiating concrete implementations:
email_svc = EmailNotification()
email_svc.connect()
email_svc.send("navneet@example.com", "System alert: Build successful.")


# ============================================================
# 5. PILLAR 3: INHERITANCE (Single, Multi-level, Multiple & super())
# ============================================================
print("\n--- 5. Pillar 3: Inheritance & super() ---")


class Vehicle:
    """Base parent class."""

    def __init__(self, brand: str, model: str, year: int):
        self.brand = brand
        self.model = model
        self.year = year

    def start(self) -> str:
        return f"{self.brand} {self.model} ({self.year}) engine turned on."

    def get_specs(self) -> str:
        return f"{self.year} {self.brand} {self.model}"


class ElectricCar(Vehicle):
    """Child subclass inheriting from Vehicle and extending behavior."""

    def __init__(self, brand: str, model: str, year: int, battery_kwh: float):
        # Call base class constructor using super()
        super().__init__(brand, model, year)
        self.battery_kwh = battery_kwh

    # Overriding start method
    def start(self) -> str:
        base_message = super().start()
        return f"{base_message} Electric powertrain silent start active (Battery: {self.battery_kwh} kWh)."


car = ElectricCar("Tesla", "Model S", 2026, 100.0)
print(car.start())
print(f"Specs: {car.get_specs()}")
print(f"isinstance(car, Vehicle): {isinstance(car, Vehicle)}")
print(f"issubclass(ElectricCar, Vehicle): {issubclass(ElectricCar, Vehicle)}")


# Multiple Inheritance and Method Resolution Order (MRO)
print("\n--- Multiple Inheritance & MRO (Method Resolution Order) ---")


class LoggerMixin:
    def log(self, message: str):
        print(f"[LOG] {message}")


class JsonSerializableMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__, default=str)


class AuditedAccount(BankAccount, LoggerMixin, JsonSerializableMixin):
    def deposit(self, amount: float) -> None:
        super().deposit(amount)
        self.log(f"Audited deposit of ${amount:,.2f} completed for {self.owner}.")


audited_acc = AuditedAccount("Navneet Saunee", 10000.0)
audited_acc.deposit(2500.0)
print(f"MRO for AuditedAccount: {[cls.__name__ for cls in AuditedAccount.__mro__]}")


# ============================================================
# 6. PILLAR 4: POLYMORPHISM & DUCK TYPING
# ============================================================
print("\n--- 6. Pillar 4: Polymorphism & Duck Typing ---")

# Polymorphism allows different classes to be treated through the same unified interface.
# Python's dynamic typing leverages "Duck Typing":
# "If it walks like a duck and quacks like a duck, it's a duck."


class PDFReport:
    def render(self) -> str:
        return "Rendering report as high-resolution PDF document."


class HTMLReport:
    def render(self) -> str:
        return "Rendering report as responsive HTML5 web page."


class MarkdownReport:
    def render(self) -> str:
        return "Rendering report as formatted GitHub-Flavored Markdown."


def generate_export(report_generator) -> None:
    """Polymorphic consumer: doesn't care about class inheritance, only the .render() interface."""
    output = report_generator.render()
    print(f"Export output: {output}")


reports = [PDFReport(), HTMLReport(), MarkdownReport()]
for r in reports:
    generate_export(r)


# ============================================================
# 7. Dunder / Magic Methods (__str__, __repr__, __len__, __eq__)
# ============================================================
print("\n--- 7. Dunder / Magic Methods ---")


class Book:
    def __init__(self, title: str, author: str, pages: int):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self) -> str:
        """User-friendly representation (used by print and str())."""
        return f"'{self.title}' by {self.author}"

    def __repr__(self) -> str:
        """Unambiguous developer representation (used in debugging/REPL)."""
        return f"Book(title='{self.title}', author='{self.author}', pages={self.pages})"

    def __len__(self) -> int:
        """Allows len(book) to return page count."""
        return self.pages

    def __eq__(self, other) -> bool:
        """Enables equality comparison with =="""
        if not isinstance(other, Book):
            return False
        return self.title == other.title and self.author == other.author


book1 = Book("Clean Code in Python", "Navneet Saunee", 380)
book2 = Book("Clean Code in Python", "Navneet Saunee", 380)
book3 = Book("Design Patterns", "GoF", 416)

print(f"str(book1) : {book1}")
print(f"repr(book1): {repr(book1)}")
print(f"len(book1) : {len(book1)} pages")
print(f"book1 == book2: {book1 == book2}")
print(f"book1 == book3: {book1 == book3}")


# ============================================================
# 8. Practical OOP Pattern: Composition over Inheritance
# ============================================================
print("\n--- 8. Composition over Inheritance ---")


class Engine:
    def __init__(self, horsepower: int):
        self.horsepower = horsepower

    def start(self) -> str:
        return f"V8 Engine running ({self.horsepower} HP)"


class Wheels:
    def __init__(self, count: int = 4):
        self.count = count

    def rotate(self) -> str:
        return f"{self.count} wheels spinning"


class SportsCar:
    """Has-a relationship: SportsCar HAS-AN Engine and HAS Wheels."""

    def __init__(self, model: str, horsepower: int):
        self.model = model
        self.engine = Engine(horsepower)
        self.wheels = Wheels(4)

    def drive(self) -> str:
        return f"{self.model} driving: {self.engine.start()} with {self.wheels.rotate()}."


sports_car = SportsCar("Apex GT", 650)
print(sports_car.drive())


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python oop_concepts.py
# ============================================================
#
# 1. ENCAPSULATION:
#    Create a class `UserProfile` with a public `username` and private `__email`.
#    Provide a `@property` getter and setter for `email` that validates the email
#    contains an '@' symbol before assignment.
#
# 2. INHERITANCE & SUPER:
#    Create a base class `EmployeeRecord(name, emp_id)` and a child class
#    `ManagerRecord(name, emp_id, team_size)`. Use `super()` in the child class
#    and add a method `display_role()` returning team size information.
#
# 3. POLYMORPHISM & ABSTRACTION:
#    Define an abstract base class `PaymentGateway(ABC)` with an `@abstractmethod`
#    named `process_payment(amount: float) -> str`.
#    Implement two concrete classes: `CreditCardPayment` and `CryptoPayment`.
#    Write a function `checkout(gateway: PaymentGateway, amount: float)` that
#    demonstrates polymorphism.
#
# 4. MAGIC METHODS:
#    Implement a `Vector2D(x, y)` class with `__str__`, `__repr__`, and `__add__`
#    methods so that `Vector2D(1, 2) + Vector2D(3, 4)` evaluates to `Vector2D(4, 6)`.

# --- write your code below this line ---
