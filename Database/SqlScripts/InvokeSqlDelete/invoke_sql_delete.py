"""
SYNOPSIS
    Runs a DELETE statement against the tenant database. Uses the sql_common
    library (Database/SqlScripts/common) for the SQL Server calls, and the shared
    db_logging helper (Database/SqlScripts/common) for logging.

DESCRIPTION
    Runs the query in --query-path against the tenant database. Connection details
    are read from --config-path; the SQL itself is read from --query-path, so
    editing that .sql file changes what gets run without touching this script.
    Double-check the WHERE clause before running - there is no dry-run mode.
    Python port of Invoke-SqlDelete.ps1.

EXAMPLE
    python invoke_sql_delete.py
    python invoke_sql_delete.py --config-path SqlDeleteConfig.json --query-path delete_query.sql

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-04
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER.parent / "common"))

#region Module Dependency Check
REQUIRED_MODULES = ["pyodbc"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

import db_logging
import sql_common


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlDeleteConfig.json"))
    parser.add_argument("--query-path", default=str(SCRIPT_FOLDER / "delete_query.sql"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    query = Path(args.query_path).read_text(encoding="utf-8")
    connection_string = sql_common.build_connection_string(config["Database"])

    rows_affected = sql_common.invoke_sql_non_query(connection_string, query)

    logger.info("Deleted %s row(s).", rows_affected)


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "invoke_sql_delete")

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, correlation_id)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, correlation_id)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, correlation_id, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
