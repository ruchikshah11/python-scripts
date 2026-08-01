"""
SYNOPSIS
    A CLI expense tracker backed by SQLite - add, list, summarize (by
    category, with an optional month filter), and delete expenses. The
    database file (expenses.db) is created automatically next to this
    script on first use.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Adjust the schema in init_db() if you need more fields (tags, currency, etc.)
    - summary --export-csv writes a CSV that ReportBuilder's build_report.py
      can turn into a formatted PDF/Excel report

EXAMPLE
    python expense_tracker.py add 45.50 --category Groceries --description "Weekly shop"
    python expense_tracker.py add 12 --category Transport --date 2026-07-01
    python expense_tracker.py list
    python expense_tracker.py list --month 2026-07
    python expense_tracker.py summary --month 2026-07
    python expense_tracker.py summary --export-csv july_summary.csv
    python expense_tracker.py delete 3

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import csv
import importlib
import logging
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # sqlite3 and csv are standard library

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"expense_tracker_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

DB_FILE = SCRIPT_FOLDER / "expenses.db"
CORRELATION_ID = str(uuid.uuid4())[:11]
#endregion

#region Logging Setup
def check_log_directory():
    LOGS_DIRECTORY.mkdir(parents=True, exist_ok=True)


def delete_old_logs(logger):
    if PURGE_LOG_DAYS <= 0:
        return
    try:
        logger.info("Deleting log files older than %s days", PURGE_LOG_DAYS)
        cutoff = datetime.now() - timedelta(days=PURGE_LOG_DAYS)
        for log_file in LOGS_DIRECTORY.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
        logger.info("Log files deleted")
    except Exception as ex:
        logger.error("Error deleting log files. Details: %s", ex)


def get_logger():
    logger = logging.getLogger("expense_tracker")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
#endregion


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("amount", type=float)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--description", default="")
    add_parser.add_argument("--date", default=None, help="YYYY-MM-DD, defaults to today")

    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("--month", default=None, help="Filter to YYYY-MM")
    list_parser.add_argument("--category", default=None, help="Filter to one category")

    summary_parser = subparsers.add_parser("summary", help="Show totals per category")
    summary_parser.add_argument("--month", default=None, help="Filter to YYYY-MM")
    summary_parser.add_argument("--export-csv", default=None, help="Also write the summary to this CSV path")

    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("id", type=int)

    return parser.parse_args()


def init_db():
    connection = sqlite3.connect(DB_FILE)
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
    connection.commit()
    return connection


def add_expense(connection, amount, category, description, expense_date, logger):
    expense_date = expense_date or datetime.now().strftime("%Y-%m-%d")
    cursor = connection.execute(
        "INSERT INTO expenses (amount, category, description, expense_date, created_at) VALUES (?, ?, ?, ?, ?)",
        (amount, category, description, expense_date, datetime.now().isoformat(timespec="seconds")),
    )
    connection.commit()
    logger.info("Added expense #%s: %.2f (%s) on %s", cursor.lastrowid, amount, category, expense_date)


def list_expenses(connection, month, category, logger):
    query = "SELECT id, amount, category, description, expense_date FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND expense_date LIKE ?"
        params.append(f"{month}%")
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY expense_date, id"

    rows = connection.execute(query, params).fetchall()
    if not rows:
        logger.info("No expenses found")
        return

    for expense_id, amount, expense_category, description, expense_date in rows:
        desc_text = f" - {description}" if description else ""
        logger.info("#%s %s %.2f [%s]%s", expense_id, expense_date, amount, expense_category, desc_text)


def summarize_expenses(connection, month, export_csv, logger):
    query = "SELECT category, SUM(amount), COUNT(*) FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND expense_date LIKE ?"
        params.append(f"{month}%")
    query += " GROUP BY category ORDER BY category"

    rows = connection.execute(query, params).fetchall()
    if not rows:
        logger.info("No expenses found")
        return

    grand_total = 0.0
    csv_rows = [("Category", "Total", "Count")]
    for category, total, count in rows:
        logger.info("%s: %.2f (%s expense(s))", category, total, count)
        grand_total += total
        csv_rows.append((category, f"{total:.2f}", count))

    logger.info("Grand total: %.2f", grand_total)
    csv_rows.append(("TOTAL", f"{grand_total:.2f}", ""))

    if export_csv:
        with open(export_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(csv_rows)
        logger.info("Summary exported to %s", export_csv)


def delete_expense(connection, expense_id, logger):
    cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    if cursor.rowcount == 0:
        raise ValueError(f"Expense #{expense_id} not found")
    logger.info("Deleted expense #%s", expense_id)


def main_process(args, logger):
    connection = init_db()
    try:
        if args.command == "add":
            add_expense(connection, args.amount, args.category, args.description, args.date, logger)
        elif args.command == "list":
            list_expenses(connection, args.month, args.category, logger)
        elif args.command == "summary":
            summarize_expenses(connection, args.month, args.export_csv, logger)
        elif args.command == "delete":
            delete_expense(connection, args.id, logger)
    finally:
        connection.close()


def main():
    args = parse_args()
    check_log_directory()
    logger = get_logger()

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        delete_old_logs(logger)
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, CORRELATION_ID)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, CORRELATION_ID)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, CORRELATION_ID, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
