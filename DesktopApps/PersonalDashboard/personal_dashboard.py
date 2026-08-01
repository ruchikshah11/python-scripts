"""
SYNOPSIS
    A single-window Tkinter "at a glance" dashboard combining current
    weather, pending to-do tasks, and this month's expense summary - all
    refreshing automatically on open. Reuses the tested functions/data
    files from Weather, TodoManager, and ExpenseTracker directly.

DESCRIPTION
    Unlike the Utility Toolbox (which wraps every tool behind tabs you
    click into), this is meant to be opened and read in one glance, then
    closed - like a home-screen widget. Weather runs on a background thread
    so the window appears immediately while it loads.

EXAMPLE
    python personal_dashboard.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-01
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import importlib
import logging
import sqlite3
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

#region Module Dependency Check
REQUIRED_MODULES = ["requests"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

PYTHON_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECTS_ROOT = PYTHON_ROOT / "Projects"
for folder_name in ["Weather", "TodoManager", "ExpenseTracker"]:
    sys.path.insert(0, str(PROJECTS_ROOT / folder_name))

import get_weather

TODO_DB = PROJECTS_ROOT / "TodoManager" / "todo.db"
EXPENSE_DB = PROJECTS_ROOT / "ExpenseTracker" / "expenses.db"
DEFAULT_LOCATION = "Zurich"


class NullLogger:
    """A do-nothing stand-in for the `logger` parameter some imported
    functions expect - the dashboard doesn't show a status/log panel."""

    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class PersonalDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Dashboard")
        self.root.geometry("480x620")
        self.logger = NullLogger()

        # --- Weather panel ---
        weather_frame = ttk.LabelFrame(root, text="Weather")
        weather_frame.pack(fill="x", padx=10, pady=10)

        location_row = ttk.Frame(weather_frame)
        location_row.pack(fill="x", padx=8, pady=(8, 0))
        ttk.Label(location_row, text="Location:").pack(side="left")
        self.location_entry = ttk.Entry(location_row, width=20)
        self.location_entry.insert(0, DEFAULT_LOCATION)
        self.location_entry.pack(side="left", padx=8)
        ttk.Button(location_row, text="Refresh", command=self.refresh_weather).pack(side="left")

        self.weather_label = ttk.Label(weather_frame, text="Loading...", justify="left")
        self.weather_label.pack(fill="x", padx=8, pady=8)

        # --- To-Do panel ---
        todo_frame = ttk.LabelFrame(root, text="To-Do (pending)")
        todo_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.todo_listbox = tk.Listbox(todo_frame, height=8)
        self.todo_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(todo_frame, text="Refresh", command=self.refresh_todo).pack(anchor="e", padx=8, pady=(0, 8))

        # --- Expense summary panel ---
        expense_frame = ttk.LabelFrame(root, text=f"Expenses ({datetime.now():%B %Y})")
        expense_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.expense_label = ttk.Label(expense_frame, text="Loading...", justify="left")
        self.expense_label.pack(fill="x", padx=8, pady=8)
        ttk.Button(expense_frame, text="Refresh", command=self.refresh_expenses).pack(anchor="e", padx=8, pady=(0, 8))

        # Load everything on open
        self.refresh_weather()
        self.refresh_todo()
        self.refresh_expenses()

    # ---------- Weather ----------

    def refresh_weather(self):
        location = self.location_entry.get().strip() or DEFAULT_LOCATION
        self.weather_label.configure(text="Loading...")

        def task():
            try:
                latitude, longitude, resolved_name, country = get_weather.geocode_location(location, self.logger)
                current, _daily = get_weather.get_weather_data(latitude, longitude, "celsius", "kmh", 1, self.logger)
                description = get_weather.WEATHER_CODE_DESCRIPTIONS.get(current["weathercode"], "Unknown")
                text = f"{resolved_name}, {country}\n{current['temperature']}C, {description}"
            except Exception as ex:
                text = f"Could not load weather: {ex}"

            self.root.after(0, lambda: self.weather_label.configure(text=text))

        threading.Thread(target=task, daemon=True).start()

    # ---------- To-Do ----------

    def refresh_todo(self):
        self.todo_listbox.delete(0, "end")
        if not TODO_DB.exists():
            self.todo_listbox.insert("end", "(no tasks yet - use TodoManager or the Toolbox GUI to add some)")
            return

        connection = sqlite3.connect(TODO_DB)
        try:
            rows = connection.execute(
                "SELECT id, text, due_date FROM tasks WHERE completed = 0 ORDER BY id"
            ).fetchall()
        finally:
            connection.close()

        if not rows:
            self.todo_listbox.insert("end", "Nothing pending - nice work")
            return

        for task_id, text, due_date in rows:
            due_text = f"  (due {due_date})" if due_date else ""
            self.todo_listbox.insert("end", f"#{task_id} {text}{due_text}")

    # ---------- Expenses ----------

    def refresh_expenses(self):
        if not EXPENSE_DB.exists():
            self.expense_label.configure(text="(no expenses yet - use ExpenseTracker or the Toolbox GUI to add some)")
            return

        current_month = datetime.now().strftime("%Y-%m")
        connection = sqlite3.connect(EXPENSE_DB)
        try:
            rows = connection.execute(
                "SELECT category, SUM(amount) FROM expenses WHERE expense_date LIKE ? GROUP BY category ORDER BY category",
                (f"{current_month}%",),
            ).fetchall()
        finally:
            connection.close()

        if not rows:
            self.expense_label.configure(text="No expenses recorded this month")
            return

        lines = [f"{category}: {total:.2f}" for category, total in rows]
        grand_total = sum(total for _category, total in rows)
        lines.append(f"Total: {grand_total:.2f}")
        self.expense_label.configure(text="\n".join(lines))


def main():
    root = tk.Tk()
    PersonalDashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
