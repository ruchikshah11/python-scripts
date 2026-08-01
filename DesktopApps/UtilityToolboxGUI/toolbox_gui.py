"""
SYNOPSIS
    A Tkinter desktop app that wraps several of the standalone CLI utilities
    built in this workspace (Weather, Currency Converter, Unit Converter,
    QR Code Generator, Password Tool, To-Do Manager, Expense Tracker) behind
    one tabbed window - reusing their tested functions directly rather than
    reimplementing the logic.

DESCRIPTION
    Each tab imports and calls the real functions from its corresponding
    tool's script (via sys.path additions to the sibling folders) - so a fix
    or improvement made in e.g. Weather/get_weather.py is picked up here too,
    nothing is duplicated. The To-Do and Expense tabs read/write the exact
    same SQLite database files as their CLI counterparts (TodoManager/todo.db,
    ExpenseTracker/expenses.db), so data stays in sync whichever way you use
    it. Network calls (Weather, Currency) run on a background thread so the
    window doesn't freeze while waiting on the API.

EXAMPLE
    python toolbox_gui.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
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
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

#region Module Dependency Check
REQUIRED_MODULES = ["PIL"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install pillow")
        sys.exit(1)

from PIL import Image, ImageTk
#endregion

#region Wire up sibling tool folders so their scripts can be imported directly
PYTHON_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECTS_ROOT = PYTHON_ROOT / "Projects"

for folder_name in ["Weather", "CurrencyConverter", "UnitConverter", "QRCodeGenerator", "PasswordTool", "TodoManager", "ExpenseTracker"]:
    sys.path.insert(0, str(PROJECTS_ROOT / folder_name))

import get_weather
import convert_currency
import convert_units
import generate_qr
import password_tool
import todo_manager
import expense_tracker
#endregion

TODO_DB = PROJECTS_ROOT / "TodoManager" / "todo.db"
EXPENSE_DB = PROJECTS_ROOT / "ExpenseTracker" / "expenses.db"


class TextWidgetLogHandler(logging.Handler):
    """A logging.Handler that appends formatted log records into a Tkinter
    Text widget, so functions imported from the CLI tools (which log status
    via `logger.info(...)`) show that status in the GUI's status panel."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        message = self.format(record)

        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", message + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

        self.text_widget.after(0, append)


class ToolboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Utility Toolbox")
        self.root.geometry("640x560")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        self.status_text = tk.Text(root, height=6, state="disabled", wrap="word")
        self.status_text.pack(fill="x", padx=8, pady=8)

        self.logger = logging.getLogger("toolbox_gui")
        self.logger.setLevel(logging.INFO)
        handler = TextWidgetLogHandler(self.status_text)
        handler.setFormatter(logging.Formatter("%(asctime)s  %(message)s", datefmt="%H:%M:%S"))
        self.logger.addHandler(handler)

        self._build_weather_tab()
        self._build_currency_tab()
        self._build_units_tab()
        self._build_qr_tab()
        self._build_password_tab()
        self._build_todo_tab()
        self._build_expense_tab()

    # ---------- helpers ----------

    def run_in_background(self, target):
        threading.Thread(target=target, daemon=True).start()

    def show_error(self, title, exception):
        self.logger.info("Error: %s", exception)
        messagebox.showerror(title, str(exception))

    # ---------- Weather ----------

    def _build_weather_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Weather")

        ttk.Label(tab, text="Location:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.weather_location = ttk.Entry(tab, width=30)
        self.weather_location.insert(0, "Zurich")
        self.weather_location.grid(row=0, column=1, padx=8, pady=8)

        self.weather_units = tk.StringVar(value="metric")
        ttk.Radiobutton(tab, text="Metric", variable=self.weather_units, value="metric").grid(row=0, column=2)
        ttk.Radiobutton(tab, text="Imperial", variable=self.weather_units, value="imperial").grid(row=0, column=3)

        ttk.Button(tab, text="Get Weather", command=self._on_get_weather).grid(row=1, column=0, padx=8, pady=8)

        self.weather_result = tk.Text(tab, height=10, width=60, state="disabled", wrap="word")
        self.weather_result.grid(row=2, column=0, columnspan=4, padx=8, pady=8)

    def _on_get_weather(self):
        location = self.weather_location.get().strip()
        units = self.weather_units.get()
        if not location:
            messagebox.showwarning("Weather", "Enter a location first")
            return

        def task():
            try:
                temperature_unit = "celsius" if units == "metric" else "fahrenheit"
                windspeed_unit = "kmh" if units == "metric" else "mph"
                temp_symbol = "C" if units == "metric" else "F"
                speed_unit = "km/h" if units == "metric" else "mph"

                latitude, longitude, resolved_name, country = get_weather.geocode_location(location, self.logger)
                current, daily = get_weather.get_weather_data(
                    latitude, longitude, temperature_unit, windspeed_unit, 5, self.logger
                )
                description = get_weather.WEATHER_CODE_DESCRIPTIONS.get(current["weathercode"], "Unknown")

                lines = [
                    f"{resolved_name}, {country}",
                    f"Now: {current['temperature']}{temp_symbol}, {description}, wind {current['windspeed']} {speed_unit}",
                    "",
                    "5-day forecast:",
                ]
                for date, code, temp_max, temp_min in zip(
                    daily["time"], daily["weathercode"], daily["temperature_2m_max"], daily["temperature_2m_min"]
                ):
                    day_description = get_weather.WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")
                    lines.append(f"  {date}: {day_description}, high {temp_max}{temp_symbol} / low {temp_min}{temp_symbol}")

                self._set_text(self.weather_result, "\n".join(lines))
            except Exception as ex:
                self.show_error("Weather", ex)

        self.run_in_background(task)

    def _set_text(self, widget, content):
        def update():
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", content)
            widget.configure(state="disabled")

        widget.after(0, update)

    # ---------- Currency ----------

    def _build_currency_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Currency")

        ttk.Label(tab, text="Amount:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.currency_amount = ttk.Entry(tab, width=15)
        self.currency_amount.insert(0, "100")
        self.currency_amount.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(tab, text="From:").grid(row=1, column=0, sticky="w", padx=8)
        self.currency_from = ttk.Entry(tab, width=8)
        self.currency_from.insert(0, "USD")
        self.currency_from.grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(tab, text="To:").grid(row=2, column=0, sticky="w", padx=8)
        self.currency_to = ttk.Entry(tab, width=8)
        self.currency_to.insert(0, "EUR")
        self.currency_to.grid(row=2, column=1, sticky="w", padx=8)

        ttk.Button(tab, text="Convert", command=self._on_convert_currency).grid(row=3, column=0, padx=8, pady=8)
        self.currency_result = ttk.Label(tab, text="")
        self.currency_result.grid(row=3, column=1, columnspan=2, sticky="w")

    def _on_convert_currency(self):
        try:
            amount = float(self.currency_amount.get())
        except ValueError:
            messagebox.showwarning("Currency", "Amount must be a number")
            return

        from_currency = self.currency_from.get().strip().upper()
        to_currency = self.currency_to.get().strip().upper()

        def task():
            try:
                if from_currency == to_currency:
                    self.currency_result.after(0, lambda: self.currency_result.configure(
                        text=f"{amount} {from_currency} = {amount} {to_currency} (same currency)"))
                    return

                result = convert_currency.convert_currency(amount, from_currency, to_currency, self.logger)
                converted = result["rates"][to_currency]
                text = f"{amount} {from_currency} = {converted} {to_currency} (as of {result['date']})"
                self.currency_result.after(0, lambda: self.currency_result.configure(text=text))
            except Exception as ex:
                self.show_error("Currency", ex)

        self.run_in_background(task)

    # ---------- Units ----------

    def _build_units_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Units")

        ttk.Label(tab, text="Category:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.unit_category = ttk.Combobox(tab, values=["length", "weight", "temperature"], state="readonly", width=15)
        self.unit_category.set("length")
        self.unit_category.grid(row=0, column=1, padx=8, pady=8)
        self.unit_category.bind("<<ComboboxSelected>>", lambda e: self._refresh_unit_choices())

        ttk.Label(tab, text="Value:").grid(row=1, column=0, sticky="w", padx=8)
        self.unit_value = ttk.Entry(tab, width=15)
        self.unit_value.insert(0, "1")
        self.unit_value.grid(row=1, column=1, padx=8)

        ttk.Label(tab, text="From:").grid(row=2, column=0, sticky="w", padx=8)
        self.unit_from = ttk.Combobox(tab, state="readonly", width=8)
        self.unit_from.grid(row=2, column=1, sticky="w", padx=8)

        ttk.Label(tab, text="To:").grid(row=3, column=0, sticky="w", padx=8)
        self.unit_to = ttk.Combobox(tab, state="readonly", width=8)
        self.unit_to.grid(row=3, column=1, sticky="w", padx=8)

        ttk.Button(tab, text="Convert", command=self._on_convert_units).grid(row=4, column=0, padx=8, pady=8)
        self.unit_result = ttk.Label(tab, text="")
        self.unit_result.grid(row=4, column=1, columnspan=2, sticky="w")

        self._refresh_unit_choices()

    def _refresh_unit_choices(self):
        category = self.unit_category.get()
        if category == "length":
            units = list(convert_units.LENGTH_TO_METERS)
        elif category == "weight":
            units = list(convert_units.WEIGHT_TO_GRAMS)
        else:
            units = convert_units.TEMPERATURE_UNITS

        self.unit_from["values"] = units
        self.unit_to["values"] = units
        self.unit_from.set(units[0])
        self.unit_to.set(units[1] if len(units) > 1 else units[0])

    def _on_convert_units(self):
        try:
            value = float(self.unit_value.get())
        except ValueError:
            messagebox.showwarning("Units", "Value must be a number")
            return

        category = self.unit_category.get()
        from_unit = self.unit_from.get()
        to_unit = self.unit_to.get()

        try:
            if category == "length":
                result = convert_units.convert_linear(value, from_unit, to_unit, convert_units.LENGTH_TO_METERS)
            elif category == "weight":
                result = convert_units.convert_linear(value, from_unit, to_unit, convert_units.WEIGHT_TO_GRAMS)
            else:
                result = convert_units.convert_temperature(value, from_unit, to_unit)

            self.unit_result.configure(text=f"{value} {from_unit} = {round(result, 6)} {to_unit}")
        except Exception as ex:
            self.show_error("Units", ex)

    # ---------- QR Code ----------

    def _build_qr_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="QR Code")

        ttk.Label(tab, text="Text or URL:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.qr_data = ttk.Entry(tab, width=40)
        self.qr_data.insert(0, "https://github.com")
        self.qr_data.grid(row=0, column=1, padx=8, pady=8)

        ttk.Button(tab, text="Generate & Save As...", command=self._on_generate_qr).grid(row=1, column=0, padx=8, pady=8)

        self.qr_image_label = ttk.Label(tab)
        self.qr_image_label.grid(row=2, column=0, columnspan=2, padx=8, pady=8)
        self._qr_photo = None  # keep a reference so Tkinter doesn't garbage-collect the image

    def _on_generate_qr(self):
        data = self.qr_data.get().strip()
        if not data:
            messagebox.showwarning("QR Code", "Enter some text or a URL first")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png")])
        if not output_path:
            return

        try:
            generate_qr.generate_qr_code(data, output_path, box_size=8, border=4)
            self.logger.info("QR code saved to %s", output_path)

            preview = Image.open(output_path)
            preview.thumbnail((200, 200))
            self._qr_photo = ImageTk.PhotoImage(preview)
            self.qr_image_label.configure(image=self._qr_photo)
        except Exception as ex:
            self.show_error("QR Code", ex)

    # ---------- Password ----------

    def _build_password_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Password")

        generate_frame = ttk.LabelFrame(tab, text="Generate")
        generate_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(generate_frame, text="Length:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.password_length = ttk.Spinbox(generate_frame, from_=4, to=64, width=5)
        self.password_length.set(16)
        self.password_length.grid(row=0, column=1, sticky="w")

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        ttk.Checkbutton(generate_frame, text="Upper", variable=self.use_upper).grid(row=1, column=0)
        ttk.Checkbutton(generate_frame, text="Lower", variable=self.use_lower).grid(row=1, column=1)
        ttk.Checkbutton(generate_frame, text="Digits", variable=self.use_digits).grid(row=1, column=2)
        ttk.Checkbutton(generate_frame, text="Symbols", variable=self.use_symbols).grid(row=1, column=3)

        ttk.Button(generate_frame, text="Generate", command=self._on_generate_password).grid(row=2, column=0, padx=8, pady=8)
        self.generated_password = ttk.Entry(generate_frame, width=30)
        self.generated_password.grid(row=2, column=1, columnspan=3, sticky="w")

        check_frame = ttk.LabelFrame(tab, text="Check Strength")
        check_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(check_frame, text="Password:").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.password_to_check = ttk.Entry(check_frame, width=30, show="*")
        self.password_to_check.grid(row=0, column=1, padx=8)

        self.show_password = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="Show", variable=self.show_password,
                        command=self._toggle_password_visibility).grid(row=0, column=2)

        ttk.Button(check_frame, text="Check", command=self._on_check_password).grid(row=1, column=0, padx=8, pady=8)
        self.password_check_result = tk.Text(check_frame, height=6, width=50, state="disabled", wrap="word")
        self.password_check_result.grid(row=2, column=0, columnspan=3, padx=8, pady=8)

    def _toggle_password_visibility(self):
        self.password_to_check.configure(show="" if self.show_password.get() else "*")

    def _on_generate_password(self):
        try:
            length = int(self.password_length.get())
            password = password_tool.generate_password(
                length, self.use_upper.get(), self.use_lower.get(), self.use_digits.get(), self.use_symbols.get()
            )
            self.generated_password.delete(0, "end")
            self.generated_password.insert(0, password)
        except Exception as ex:
            self.show_error("Password", ex)

    def _on_check_password(self):
        password = self.password_to_check.get()
        if not password:
            messagebox.showwarning("Password", "Enter a password to check first")
            return

        score, label, feedback = password_tool.score_password(password)
        lines = [f"Score: {score}/100 ({label})"] + [f"- {line}" for line in feedback]
        self._set_text(self.password_check_result, "\n".join(lines))

    # ---------- To-Do ----------

    def _build_todo_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="To-Do")

        entry_frame = ttk.Frame(tab)
        entry_frame.pack(fill="x", padx=8, pady=8)
        ttk.Label(entry_frame, text="New task:").pack(side="left")
        self.todo_entry = ttk.Entry(entry_frame, width=40)
        self.todo_entry.pack(side="left", padx=8)
        ttk.Button(entry_frame, text="Add", command=self._on_add_task).pack(side="left")

        self.todo_listbox = tk.Listbox(tab, height=15)
        self.todo_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        button_frame = ttk.Frame(tab)
        button_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(button_frame, text="Complete Selected", command=self._on_complete_task).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Delete Selected", command=self._on_delete_task).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Refresh", command=self._refresh_todo_list).pack(side="left", padx=4)

        self._todo_ids = []  # parallel list mapping Listbox row -> task id
        self._refresh_todo_list()

    def _get_todo_connection(self):
        TODO_DB.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(TODO_DB)

    def _refresh_todo_list(self):
        connection = self._get_todo_connection()
        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    due_date TEXT,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            rows = connection.execute(
                "SELECT id, text, due_date, completed FROM tasks WHERE completed = 0 ORDER BY id"
            ).fetchall()
        finally:
            connection.close()

        self.todo_listbox.delete(0, "end")
        self._todo_ids = []
        for task_id, text, due_date, _completed in rows:
            due_text = f"  (due {due_date})" if due_date else ""
            self.todo_listbox.insert("end", f"#{task_id} {text}{due_text}")
            self._todo_ids.append(task_id)

    def _on_add_task(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
        try:
            connection = self._get_todo_connection()
            todo_manager.add_task(connection, text, None, self.logger)
            connection.close()
            self.todo_entry.delete(0, "end")
            self._refresh_todo_list()
        except Exception as ex:
            self.show_error("To-Do", ex)

    def _selected_todo_id(self):
        selection = self.todo_listbox.curselection()
        if not selection:
            messagebox.showinfo("To-Do", "Select a task first")
            return None
        return self._todo_ids[selection[0]]

    def _on_complete_task(self):
        task_id = self._selected_todo_id()
        if task_id is None:
            return
        try:
            connection = self._get_todo_connection()
            todo_manager.complete_task(connection, task_id, self.logger)
            connection.close()
            self._refresh_todo_list()
        except Exception as ex:
            self.show_error("To-Do", ex)

    def _on_delete_task(self):
        task_id = self._selected_todo_id()
        if task_id is None:
            return
        try:
            connection = self._get_todo_connection()
            todo_manager.delete_task(connection, task_id, self.logger)
            connection.close()
            self._refresh_todo_list()
        except Exception as ex:
            self.show_error("To-Do", ex)

    # ---------- Expenses ----------

    def _build_expense_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Expenses")

        entry_frame = ttk.Frame(tab)
        entry_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(entry_frame, text="Amount:").grid(row=0, column=0, sticky="w")
        self.expense_amount = ttk.Entry(entry_frame, width=10)
        self.expense_amount.grid(row=0, column=1, padx=4)

        ttk.Label(entry_frame, text="Category:").grid(row=0, column=2, sticky="w")
        self.expense_category = ttk.Entry(entry_frame, width=15)
        self.expense_category.grid(row=0, column=3, padx=4)

        ttk.Label(entry_frame, text="Description:").grid(row=0, column=4, sticky="w")
        self.expense_description = ttk.Entry(entry_frame, width=20)
        self.expense_description.grid(row=0, column=5, padx=4)

        ttk.Button(entry_frame, text="Add", command=self._on_add_expense).grid(row=0, column=6, padx=8)

        self.expense_listbox = tk.Listbox(tab, height=12)
        self.expense_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        button_frame = ttk.Frame(tab)
        button_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(button_frame, text="Refresh", command=self._refresh_expense_list).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Show Summary", command=self._on_show_expense_summary).pack(side="left", padx=4)

        self.expense_summary_label = ttk.Label(tab, text="", justify="left")
        self.expense_summary_label.pack(fill="x", padx=8, pady=(0, 8))

        self._refresh_expense_list()

    def _get_expense_connection(self):
        EXPENSE_DB.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(EXPENSE_DB)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        return connection

    def _refresh_expense_list(self):
        connection = self._get_expense_connection()
        try:
            rows = connection.execute(
                "SELECT id, amount, category, description, expense_date FROM expenses ORDER BY expense_date DESC, id DESC LIMIT 50"
            ).fetchall()
        finally:
            connection.close()

        self.expense_listbox.delete(0, "end")
        for expense_id, amount, category, description, expense_date in rows:
            desc_text = f" - {description}" if description else ""
            self.expense_listbox.insert("end", f"#{expense_id} {expense_date}  {amount:.2f} [{category}]{desc_text}")

    def _on_add_expense(self):
        try:
            amount = float(self.expense_amount.get())
        except ValueError:
            messagebox.showwarning("Expenses", "Amount must be a number")
            return

        category = self.expense_category.get().strip()
        if not category:
            messagebox.showwarning("Expenses", "Category is required")
            return
        description = self.expense_description.get().strip()

        try:
            connection = self._get_expense_connection()
            expense_tracker.add_expense(connection, amount, category, description, None, self.logger)
            connection.close()
            self.expense_amount.delete(0, "end")
            self.expense_category.delete(0, "end")
            self.expense_description.delete(0, "end")
            self._refresh_expense_list()
        except Exception as ex:
            self.show_error("Expenses", ex)

    def _on_show_expense_summary(self):
        connection = self._get_expense_connection()
        try:
            rows = connection.execute(
                "SELECT category, SUM(amount), COUNT(*) FROM expenses GROUP BY category ORDER BY category"
            ).fetchall()
        finally:
            connection.close()

        if not rows:
            self.expense_summary_label.configure(text="No expenses recorded yet")
            return

        lines = [f"{category}: {total:.2f} ({count} expense(s))" for category, total, count in rows]
        grand_total = sum(total for _category, total, _count in rows)
        lines.append(f"Grand total: {grand_total:.2f}")
        self.expense_summary_label.configure(text="\n".join(lines))


def main():
    root = tk.Tk()
    ToolboxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
