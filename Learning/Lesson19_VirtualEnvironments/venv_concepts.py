"""
SYNOPSIS
    Lesson 19: Virtual Environments & Package Management in Python -
    Why virtual environments are essential (dependency isolation, conflicting versions),
    creating environments via venv (`python -m venv .venv`), activation and
    deactivation across OS platforms (bash, zsh, PowerShell, Windows cmd),
    inspecting active environment paths (sys.prefix vs sys.base_prefix),
    pip dependency pinning (requirements.txt, pip freeze), modern tools
    (pip, poetry, pipenv, uv), and .gitignore best practices.

DESCRIPTION
    Run this file top-to-bottom to inspect your current Python runtime environment,
    detect if you are running inside a virtual environment, and demonstrate
    reproducible environment inspection.

EXAMPLE
    python venv_concepts.py

NOTES
    Created by  : Navneet Saunee
    Created on  : 2026-11-15
    Modified by : Navneet Saunee
    Modified on : 2026-11-15
    Version     : 1.0.0
"""

import sys
import os
import site
import subprocess

print("=" * 60)
print("LESSON 19: Python Virtual Environments & Dependency Management")
print("=" * 60)


# ============================================================
# 1. Inspecting Python Environment Paths
# ============================================================
print("\n--- 1. Python Environment Inspection ---")
print(f"Current Python Executable : {sys.executable}")
print(f"Python Version            : {sys.version.split()[0]}")
print(f"Active sys.prefix         : {sys.prefix}")
print(f"Base sys.base_prefix      : {sys.base_prefix}")

# How Python detects if it is running inside a virtual environment:
# If sys.prefix != sys.base_prefix, Python is executing inside a virtual environment!
is_venv = sys.prefix != sys.base_prefix
print(f"Running inside a Virtual Environment? -> {is_venv}")

if is_venv:
    print("  [INFO] Virtual environment is ACTIVE.")
else:
    print("  [INFO] Currently running using system/global Python installation.")


# ============================================================
# 2. Package Site-Packages Directories
# ============================================================
print("\n--- 2. Where Installed Packages Live (site-packages) ---")
site_packages = site.getsitepackages()
for idx, path in enumerate(site_packages, 1):
    print(f"  [{idx}] {path}")


# ============================================================
# 3. Virtual Environment Lifecycle Walkthrough
# ============================================================
print("\n--- 3. Virtual Environment Command Reference ---")
print(
    """
1. CREATE a virtual environment named '.venv':
   python3 -m venv .venv

2. ACTIVATE the environment:
   - Linux / macOS (bash/zsh):
       source .venv/bin/activate
   - Windows (PowerShell):
       .venv\\Scripts\\Activate.ps1
   - Windows (Command Prompt):
       .venv\\Scripts\\activate.bat

3. VERIFY activation:
   which python    (Linux/macOS)
   where python    (Windows)

4. INSTALL dependencies:
   pip install requests pytest

5. EXPORT pinned dependencies:
   pip freeze > requirements.txt

6. REPRODUCE on another machine:
   pip install -r requirements.txt

7. DEACTIVATE when done:
   deactivate
"""
)


# ============================================================
# 4. Dependency Pinning & requirements.txt Best Practices
# ============================================================
print("\n--- 4. Dependency Pinning Formats ---")
print("Sample requirements.txt entries:")
print("  requests==2.31.0       # Exact pin (safest for production deployments)")
print("  pytest>=8.0.0,<9.0.0   # Semantic range (compatible releases)")
print("  black~=24.1.0          # Compatible release clause")
print("  -r dev-requirements.txt# Chaining requirement files")


# ============================================================
# 5. Programmatic Environment Audit Function
# ============================================================
print("\n--- 5. Programmatic Environment Audit ---")


def audit_environment():
    """Returns a health summary of the current Python environment."""
    return {
        "executable": sys.executable,
        "is_virtual_env": sys.prefix != sys.base_prefix,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "user_site_enabled": site.ENABLE_USER_SITE,
        "sys_path_entries_count": len(sys.path),
    }


env_report = audit_environment()
for key, value in env_report.items():
    print(f"  {key:<24}: {value}")


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python venv_concepts.py
# ============================================================
#
# 1. PARSE REQUIREMENTS:
#    Write a function `parse_requirements(text)` that takes multi-line string
#    content from a simulated requirements.txt, strips comments ('#') and
#    blank lines, and returns a dictionary of `{package_name: version}`.
#    Test on:
#      requests==2.31.0
#      # Testing framework
#      pytest==8.1.1
#      flask==3.0.0
#
# 2. VENV DETECTOR:
#    Write a function `assert_venv_active()` that raises a `RuntimeError`
#    if `sys.prefix == sys.base_prefix`, with message "Must run within a virtualenv!".

# --- write your code below this line ---
