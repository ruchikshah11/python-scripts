"""
SYNOPSIS
    Bulk-imports a CSV file into a table in the tenant database. Uses the
    sql_common library (Database/SqlScripts/common) for the SQL Server calls, and
    the shared db_logging helper (Database/SqlScripts/common) for logging.

DESCRIPTION
    Reads --csv-path and bulk-inserts its rows into config["TableName"] via a
    parameterized, fast_executemany INSERT (the Python equivalent of SqlBulkCopy).
    The CSV's header row must match the destination table's column names.
    Connection details, target table, and whether to truncate first are read from
    --config-path. This is the reverse of Export-SqlQueryToCsv.
    Python port of Import-CsvToSql.ps1.

EXAMPLE
    python import_csv_to_sql.py
    python import_csv_to_sql.py --config-path SqlImportConfig.json --csv-path import_data.csv

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
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlImportConfig.json"))
    parser.add_argument("--csv-path", default=str(SCRIPT_FOLDER / "import_data.csv"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    connection_string = sql_common.build_connection_string(config["Database"])

    with open(args.csv_path, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        logger.info("No rows found in %s.", args.csv_path)
        return

    if config.get("TruncateBeforeImport"):
        sql_common.invoke_sql_non_query(connection_string, f"TRUNCATE TABLE {config['TableName']}")

    sql_common.bulk_insert(connection_string, config["TableName"], rows)

    logger.info("Imported %s row(s) from %s into %s.", len(rows), args.csv_path, config["TableName"])


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "import_csv_to_sql")

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
