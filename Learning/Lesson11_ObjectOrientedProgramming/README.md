# Lesson 11: Object-Oriented Programming (OOP) in Python

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering the core foundations of Object-Oriented Programming (OOP) in Python, with detailed focus on all **Four Pillars of OOP** (Encapsulation, Abstraction, Inheritance, and Polymorphism), method types (`instance`, `@classmethod`, `@staticmethod`), property decorators, magic methods, and architecture design patterns.

---

## 1. Introduction

Object-Oriented Programming (OOP) is a programming paradigm based on the concept of **objects**, which contain data (attributes/properties) and code (methods/functions). Python is fully object-oriented and supports multiple inheritance, duck typing, and metaprogramming.

### Why OOP?
- **Modularity**: Organizes complex codebases into distinct, self-contained units.
- **Reusability**: Allows code extension through inheritance and mixins without duplicating logic.
- **Maintainability**: Enforces controlled access and abstraction boundaries.
- **Real-World Modeling**: Maps domain entities (e.g., Accounts, Services, Vehicles) directly to software components.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Define **Classes** and instantiate **Objects** with `__init__` and `self`.
2. Differentiate between **Class attributes** and **Instance attributes**.
3. Use **Instance methods**, `@classmethod` (alternative constructors), and `@staticmethod` (utility functions).
4. Master **Pillar 1: Encapsulation** using public, protected (`_`), private (`__`) attributes, and `@property` decorators.
5. Master **Pillar 2: Abstraction** using Abstract Base Classes (`abc.ABC`) and `@abstractmethod`.
6. Master **Pillar 3: Inheritance**, method overriding, `super()`, multiple inheritance, and Method Resolution Order (`MRO`).
7. Master **Pillar 4: Polymorphism** and Python's dynamic **Duck Typing** philosophy.
8. Implement fundamental **Magic/Dunder Methods** (`__str__`, `__repr__`, `__len__`, `__eq__`, `__add__`).
9. Compare and apply **Composition vs. Inheritance** ("Has-a" vs. "Is-a").
10. Solve real-world OOP problems and interview challenges.

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. The Four Pillars of OOP](#4-the-four-pillars-of-oop)
  - [4.1 Pillar 1: Encapsulation](#41-pillar-1-encapsulation)
  - [4.2 Pillar 2: Abstraction](#42-pillar-2-abstraction)
  - [4.3 Pillar 3: Inheritance](#43-pillar-3-inheritance)
  - [4.4 Pillar 4: Polymorphism](#44-pillar-4-polymorphism)
- [5. Core OOP Concepts](#5-core-oop-concepts)
  - [5.1 Classes, Objects, and `self`](#51-classes-objects-and-self)
  - [5.2 Class vs. Instance Attributes](#52-class-vs-instance-attributes)
  - [5.3 Method Types: Instance, Class, and Static](#53-method-types-instance-class-and-static)
  - [5.4 Dunder (Magic) Methods](#54-dunder-magic-methods)
  - [5.5 Composition over Inheritance](#55-composition-over-inheritance)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. The Four Pillars of OOP

```
                   +-------------------------------+
                   |      THE 4 PILLARS OF OOP     |
                   +-------------------------------+
                     /             |             \
       +------------+        +-----+------+        +------------+
       |             \      /              \      /             |
+--------------+ +--------------+ +---------------+ +---------------+
| Encapsulation| |  Abstraction | |  Inheritance  | |  Polymorphism |
| Data hiding  | | Hide complex | | Code reuse    | | Many forms    |
| & properties | | internals    | | & super()     | | & Duck Typing |
+--------------+ +--------------+ +---------------+ +---------------+
```

### 4.1 Pillar 1: Encapsulation
Encapsulation bundles data and the methods that mutate that data together within a class, while restricting direct external access to prevent unintended corruption.

- **Public**: `self.name` (accessible from anywhere)
- **Protected**: `self._account_type` (convention indicating internal or subclass use only)
- **Private**: `self.__balance` (name-mangled to `_ClassName__balance` by Python)
- **Property Decorators**: `@property`, `@<attr>.setter`, `@<attr>.deleter` provide Pythonic getters and setters with validation logic.

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.__balance = balance  # Private

    @property
    def balance(self) -> float:
        return self.__balance

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.__balance += amount
```

### 4.2 Pillar 2: Abstraction
Abstraction focuses on **what** an object does rather than **how** it does it. It hides low-level complexity behind a simplified, unified interface.

In Python, abstraction is enforced using the standard library module `abc` with `ABC` and `@abstractmethod`:
- Subclasses **must** provide concrete implementations of all `@abstractmethod`s, or Python raises a `TypeError` at instantiation time.

```python
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Subclasses must implement send()."""
        pass
```

### 4.3 Pillar 3: Inheritance
Inheritance enables a child class to inherit attributes and methods from a parent class, promoting code reuse and modular hierarchies ("Is-a" relationship).

- **`super()`**: Calls methods on the parent class without hardcoding the parent's name.
- **Method Overriding**: Modifying or extending base class behavior in child classes.
- **Multiple Inheritance & MRO**: Python uses the C3 Linearization algorithm to determine method resolution order (`ClassName.__mro__`).

```python
class Vehicle:
    def __init__(self, brand: str):
        self.brand = brand

class ElectricCar(Vehicle):
    def __init__(self, brand: str, battery_kwh: float):
        super().__init__(brand)
        self.battery_kwh = battery_kwh
```

### 4.4 Pillar 4: Polymorphism
Polymorphism allows different classes to respond to the same method invocation in their own unique way.

Python embraces **Duck Typing**: *"If it walks like a duck and quacks like a duck, it's a duck."* Functions do not need static type constraints—they only require the passed object to implement the required method or attribute.

```python
class PDFReport:
    def render(self): return "PDF Content"

class HTMLReport:
    def render(self): return "HTML Content"

def export(report):
    print(report.render())  # Works for any object with a .render() method
```

---

## 5. Core OOP Concepts

### 5.1 Classes, Objects, and `self`
- A **Class** is a blueprint for creating objects.
- An **Object** is a concrete instance of a class.
- `self` refers to the specific instance being operated on.

### 5.2 Class vs. Instance Attributes
- **Class attributes** belong to the class itself and are shared by all instances.
- **Instance attributes** belong exclusively to the specific object instance created via `self.x = ...`.

### 5.3 Method Types: Instance, Class, and Static

| Method Type | Decorator | First Parameter | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Instance Method** | None | `self` | Access and modify instance-level state |
| **Class Method** | `@classmethod` | `cls` | Factory methods, alternative constructors, class state |
| **Static Method** | `@staticmethod` | None | Self-contained utility functions logically grouped in the class |

### 5.4 Dunder (Magic) Methods
Special methods enclosed in double underscores customize built-in Python behaviors:
- `__str__(self)`: Human-readable string representation (for `print()` and `str()`).
- `__repr__(self)`: Unambiguous developer string representation (for debugging).
- `__len__(self)`: Enables `len(obj)`.
- `__eq__(self, other)`: Enables equality comparison `==`.
- `__add__(self, other)`: Enables addition operator `+`.

### 5.5 Composition over Inheritance
- **Inheritance ("Is-a")**: `ElectricCar` is a `Vehicle`. Use when the child class is a specialized type of the parent.
- **Composition ("Has-a")**: `Car` has an `Engine` and has `Wheels`. Prefer composition to build flexible architectures without deep, fragile inheritance trees.

---

## 6. Frequently Asked Interview Questions

### Q1: What are the four pillars of OOP and how does Python implement them?
**Answer**:
1. **Encapsulation**: Grouping data and methods, using `_` (protected convention), `__` (name mangling for private members), and `@property` getters/setters.
2. **Abstraction**: Hiding internal implementation using `abc.ABC` and `@abstractmethod`.
3. **Inheritance**: Deriving child classes from parent classes using `class Child(Parent):` and `super()`.
4. **Polymorphism**: Treating different types uniformly via Duck Typing and method overriding.

### Q2: What is the difference between `@classmethod` and `@staticmethod`?
**Answer**:
- `@classmethod` receives the class object (`cls`) as its first parameter. It can access and modify class state and is commonly used as an alternative constructor (e.g. `Employee.from_string(...)`).
- `@staticmethod` does not receive `self` or `cls`. It is a normal utility function that logically belongs inside the class namespace but does not access instance or class state.

### Q3: What is Method Resolution Order (MRO) in Python?
**Answer**:
MRO defines the search order Python follows to locate an attribute or method in a class hierarchy, especially with multiple inheritance. Python uses the **C3 Linearization** algorithm. You can inspect it using `Class.__mro__` or `Class.mro()`.

### Q4: Does Python support true private variables?
**Answer**:
Not in the strict C++/Java sense. When you prefix an attribute with double underscores (e.g. `__balance`), Python performs **name mangling**, renaming it internally to `_ClassName__balance`. This prevents accidental collisions in subclasses, but can still be accessed directly if intentionally referenced as `obj._ClassName__balance`.

### Q5: When should you choose Composition over Inheritance?
**Answer**:
Favor composition when you need runtime flexibility, when components do not share an "is-a" taxonomy, or to avoid rigid inheritance hierarchies that break when requirements change. Composition models "has-a" relationships (e.g., a `Computer` has a `CPU` and `RAM`).

---

## 7. How to Run

Run the lesson script directly from terminal:
```bash
python oop_concepts.py
```

---

## 8. Exercises

At the bottom of [oop_concepts.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson11_ObjectOrientedProgramming/oop_concepts.py):
1. **Encapsulation**: Create a `UserProfile` class with a private `__email` attribute and a `@property` setter that validates the email string contains `'@'`.
2. **Inheritance & `super()`**: Create a base class `EmployeeRecord` and a child class `ManagerRecord` that calls `super().__init__()` and adds a `display_role()` method.
3. **Polymorphism & Abstraction**: Define an abstract base class `PaymentGateway(ABC)` with `@abstractmethod` `process_payment(amount)`. Implement `CreditCardPayment` and `CryptoPayment`, and write a polymorphic `checkout` function.
4. **Magic Methods**: Implement `Vector2D(x, y)` supporting `__str__`, `__repr__`, and vector addition `__add__`.

---

## 9. Completion Checklist

- [ ] Run `python oop_concepts.py` and inspect all module outputs.
- [ ] Understand all 4 OOP pillars (Encapsulation, Abstraction, Inheritance, Polymorphism).
- [ ] Implement exercise 1 (Encapsulation with `@property`).
- [ ] Implement exercise 2 (Inheritance & `super()`).
- [ ] Implement exercise 3 (Abstraction with `ABC` & Polymorphic checkout).
- [ ] Implement exercise 4 (Magic methods & operator overloading).
- [ ] Review all interview questions and answers.
