# Lesson 19: Python Virtual Environments & Dependency Management

**Author**: Navneet Saunee  
**Date**: November 2026  

A comprehensive guide and runnable reference script covering Python virtual environment creation, activation, inspection, package isolation, dependency management with `pip` and `requirements.txt`, modern tooling (`venv`, `poetry`, `uv`), and `.gitignore` best practices.

---

## 1. Introduction

When developing Python applications, different projects often require incompatible versions of the same external library (e.g. Project A needs `Django 3.2`, Project B needs `Django 5.0`).

Installing packages globally directly into the system Python (`/usr/lib/python...` or `C:\Python...`) causes dependency conflicts, permission errors, and risks breaking operating system tools that rely on specific Python libraries.

A **Virtual Environment** is an isolated folder structure containing its own Python executable, standard library links, and private `site-packages` directory.

---

## 2. Learning Objectives

By completing this module, you will be able to:
1. Explain why virtual environments are mandatory for clean Python development.
2. Create isolated environments using the standard library `venv` module.
3. Activate and deactivate environments across Linux, macOS, and Windows.
4. Programmatically inspect environment paths (`sys.prefix` vs `sys.base_prefix`).
5. Install, upgrade, and manage packages using `pip`.
6. Freeze and replicate dependencies using `requirements.txt`.
7. Configure `.gitignore` to avoid committing virtual environment folders.
8. Understand modern Python package management tools (`pip`, `poetry`, `pipenv`, `uv`).

---

## 3. Table of Contents

- [1. Introduction](#1-introduction)
- [2. Learning Objectives](#2-learning-objectives)
- [3. Table of Contents](#3-table-of-contents)
- [4. Virtual Environment Mechanics](#4-virtual-environment-mechanics)
  - [4.1 Creation with `venv`](#41-creation-with-venv)
  - [4.2 Cross-Platform Activation](#42-cross-platform-activation)
  - [4.3 How Python Detects a Virtual Environment](#43-how-python-detects-a-virtual-environment)
  - [4.4 Dependency Management with `pip`](#44-dependency-management-with-pip)
  - [4.5 Pinning Dependencies with `requirements.txt`](#45-pinning-dependencies-with-requirementstxt)
  - [4.6 `.gitignore` Best Practices](#46-gitignore-best-practices)
- [5. Modern Tooling Landscape](#5-modern-tooling-landscape)
- [6. Frequently Asked Interview Questions](#6-frequently-asked-interview-questions)
- [7. How to Run](#7-how-to-run)
- [8. Exercises](#8-exercises)
- [9. Completion Checklist](#9-completion-checklist)

---

## 4. Virtual Environment Mechanics

### 4.1 Creation with `venv`
The `venv` module has been built into Python since version 3.3:
```bash
# General syntax: python -m venv <directory_name>
python3 -m venv .venv
```
This generates a `.venv/` directory containing:
- `pyvenv.cfg` configuration file
- `bin/` (Linux/macOS) or `Scripts/` (Windows) with python binaries and activation scripts
- `lib/pythonX.Y/site-packages` for isolated library installations

### 4.2 Cross-Platform Activation

| Operating System | Shell | Activation Command |
| :--- | :--- | :--- |
| **Linux / macOS** | Bash / Zsh | `source .venv/bin/activate` |
| **Linux / macOS** | Fish | `source .venv/bin/activate.fish` |
| **Windows** | PowerShell | `.venv\Scripts\Activate.ps1` |
| **Windows** | Command Prompt (`cmd`) | `.venv\Scripts\activate.bat` |
| **Any OS** | Any Shell (Deactivate) | `deactivate` |

### 4.3 How Python Detects a Virtual Environment
When Python boots, it compares `sys.prefix` with `sys.base_prefix`:
- In standard system Python: `sys.prefix == sys.base_prefix`
- In a virtual environment: `sys.prefix != sys.base_prefix` (`sys.prefix` points to `.venv`)

### 4.4 Dependency Management with `pip`
```bash
# Install a package
pip install requests

# Upgrade a package
pip install --upgrade requests

# Show installed package details
pip show requests
```

### 4.5 Pinning Dependencies with `requirements.txt`
```bash
# Save current environment state:
pip freeze > requirements.txt

# Recreate environment on a new machine / CI pipeline:
pip install -r requirements.txt
```

### 4.6 `.gitignore` Best Practices
Never commit virtual environment folders or installed binaries to Git. Add the following to your `.gitignore`:
```gitignore
# Virtual Environments
.venv/
venv/
env/
ENV/
*.pyc
__pycache__/
```

---

## 5. Modern Tooling Landscape

| Tool | Type | Key Features |
| :--- | :--- | :--- |
| **`venv` + `pip`** | Standard Library | Built-in, ubiquitous, zero external installation |
| **`poetry`** | Third-Party | Deterministic lockfiles (`poetry.lock`), dependency resolution, packaging |
| **`pipenv`** | Third-Party | Combines `Pipfile` and `Pipfile.lock` with automatic virtualenv management |
| **`uv`** | High Performance | Written in Rust by Astral; 10x-100x faster than standard `pip` |

---

## 6. Frequently Asked Interview Questions

### Q1: Why should you never commit a virtual environment directory to version control?
**Answer**:
1. Virtual environments contain platform-specific compiled binaries and symlinks that will not execute on machines running other operating systems or CPU architectures.
2. They drastically bloat repository sizes with thousands of third-party files.
3. Dependencies should be documented declaratively in `requirements.txt` or `pyproject.toml` so team members can install clean, reproducible environments.

### Q2: What is `pyvenv.cfg` and what role does it play?
**Answer**:
`pyvenv.cfg` is the core configuration file located at the root of every virtual environment. It specifies the path to the base system Python executable (`home = ...`) and whether global site-packages should be accessible (`include-system-site-packages = false`).

### Q3: What is the difference between `pip freeze` and hand-crafted `requirements.txt`?
**Answer**:
`pip freeze` lists every single package installed in the environment with exact `==` versions, including all transitive (sub-)dependencies. A hand-crafted `requirements.txt` typically lists only top-level direct project dependencies, often with version ranges (e.g. `requests>=2.28`).

---

## 7. How to Run

Run the environment audit script directly:
```bash
python venv_concepts.py
```

---

## 8. Exercises

In [venv_concepts.py](file:///mnt/c/Users/saune/Projects/python-scripts/Learning/Lesson19_VirtualEnvironments/venv_concepts.py):
1. **Requirements Parser**: Implement `parse_requirements(text)` to sanitize comments and parse `{package: version}` pairs.
2. **Environment Guard**: Implement `assert_venv_active()` that raises an exception if running outside an active virtual environment.

---

## 9. Completion Checklist

- [ ] Run `python venv_concepts.py` and inspect your current Python paths.
- [ ] Practice creating and activating a `.venv` locally.
- [ ] Practice exporting and installing from `requirements.txt`.
- [ ] Complete exercise 1 (Requirements parser).
- [ ] Complete exercise 2 (Virtualenv guard).
- [ ] Review all interview questions and the tooling landscape.
