"""
SYNOPSIS
    Runs a SQL query against the tenant database and exports the results to CSV.
    Uses the sql_common library (Database/SqlScripts/common) for the SQL Server
    calls, and the shared db_logging helper (Database/SqlScripts/common) for logging.

DESCRIPTION
    Runs the query in --query-path against the tenant database and exports the
    results to CSV. Connection details are read from --config-path; the SQL itself
    is read from --query-path, so editing that .sql file changes what gets run
    without touching this script. Python port of Export-SqlQueryToCsv.ps1.

EXAMPLE
    python export_sql_query_to_csv.py
    python export_sql_query_to_csv.py --config-path SqlExportConfig.json --query-path effort_query.sql

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-04
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import csv
import importlib
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER.parent / "common"))

#region Module Dependency Check
REQUIRED_MODULES = ["pyodbc"]  # csv is standard library

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
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlExportConfig.json"))
    parser.add_argument("--query-path", default=str(SCRIPT_FOLDER / "effort_query.sql"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    query = Path(args.query_path).read_text(encoding="utf-8")
    connection_string = sql_common.build_connection_string(config["Database"])

    columns, rows = sql_common.invoke_sql_query(connection_string, query)

    output_path = Path(config["OutputPath"])
    if not output_path.is_absolute():
        output_path = SCRIPT_FOLDER / output_path

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Exported %s rows to %s", len(rows), output_path)


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "export_sql_query_to_csv")

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
