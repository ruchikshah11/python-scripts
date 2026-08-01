"""
SYNOPSIS
    A CLI to-do list manager backed by SQLite - add, list, complete, and
    delete tasks. The database file (todo.db) is created automatically next
    to this script on first use.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Adjust the schema in init_db() if you need more fields (priority, tags, etc.)

EXAMPLE
    python todo_manager.py add "Buy milk"
    python todo_manager.py add "Finish report" --due 2026-08-01
    python todo_manager.py list
    python todo_manager.py list --all
    python todo_manager.py complete 2
    python todo_manager.py delete 3

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import logging
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # sqlite3 is standard library

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"todo_manager_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

DB_FILE = SCRIPT_FOLDER / "todo.db"
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
    logger = logging.getLogger("todo_manager")
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

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("text", help="Task description")
    add_parser.add_argument("--due", default=None, help="Due date, e.g. 2026-08-01")

    list_parser = subparsers.add_parser("list", help="List tasks (pending only, by default)")
    list_parser.add_argument("--all", action="store_true", help="Show completed tasks too")
    list_parser.add_argument("--completed", action="store_true", help="Show only completed tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("id", type=int)

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int)

    return parser.parse_args()


def init_db():
    connection = sqlite3.connect(DB_FILE)
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
    connection.commit()
    return connection


def add_task(connection, text, due_date, logger):
    cursor = connection.execute(
        "INSERT INTO tasks (text, due_date, created_at) VALUES (?, ?, ?)",
        (text, due_date, datetime.now().isoformat(timespec="seconds")),
    )
    connection.commit()
    logger.info("Added task #%s: %s", cursor.lastrowid, text)


def list_tasks(connection, show_all, show_completed_only, logger):
    if show_completed_only:
        query = "SELECT id, text, due_date, completed, completed_at FROM tasks WHERE completed = 1 ORDER BY id"
    elif show_all:
        query = "SELECT id, text, due_date, completed, completed_at FROM tasks ORDER BY id"
    else:
        query = "SELECT id, text, due_date, completed, completed_at FROM tasks WHERE completed = 0 ORDER BY id"

    rows = connection.execute(query).fetchall()
    if not rows:
        logger.info("No tasks found")
        return

    for row in rows:
        task_id, text, due_date, completed, completed_at = row
        status = "[x]" if completed else "[ ]"
        due_text = f" (due {due_date})" if due_date else ""
        completed_text = f" (completed {completed_at})" if completed else ""
        logger.info("%s #%s %s%s%s", status, task_id, text, due_text, completed_text)


def complete_task(connection, task_id, logger):
    cursor = connection.execute(
        "UPDATE tasks SET completed = 1, completed_at = ? WHERE id = ? AND completed = 0",
        (datetime.now().isoformat(timespec="seconds"), task_id),
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise ValueError(f"Task #{task_id} not found, or already completed")
    logger.info("Completed task #%s", task_id)


def delete_task(connection, task_id, logger):
    cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    if cursor.rowcount == 0:
        raise ValueError(f"Task #{task_id} not found")
    logger.info("Deleted task #%s", task_id)


def main_process(args, logger):
    connection = init_db()
    try:
        if args.command == "add":
            add_task(connection, args.text, args.due, logger)
        elif args.command == "list":
            list_tasks(connection, args.all, args.completed, logger)
        elif args.command == "complete":
            complete_task(connection, args.id, logger)
        elif args.command == "delete":
            delete_task(connection, args.id, logger)
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
