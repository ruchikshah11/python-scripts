"""
SYNOPSIS
    Runs a multi-batch .sql file (e.g. a migration script) against the tenant
    database. Uses the sql_common library (Database/SqlScripts/common) for the SQL
    Server calls, and the shared db_logging helper (Database/SqlScripts/common) for
    logging.

DESCRIPTION
    Splits --script-path on lines containing only "GO" and runs each batch in turn,
    the same way SSMS would. Use this instead of the single-statement
    invoke_sql_*.py scripts when a script needs multiple batches (e.g. DDL followed
    by DML, or statements that must run in separate batches).
    Python port of Invoke-SqlScriptFile.ps1.

EXAMPLE
    python invoke_sql_script_file.py
    python invoke_sql_script_file.py --config-path SqlScriptFileConfig.json --script-path migration_script.sql

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-04
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import re
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
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlScriptFileConfig.json"))
    parser.add_argument("--script-path", default=str(SCRIPT_FOLDER / "migration_script.sql"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    connection_string = sql_common.build_connection_string(config["Database"])
    script_text = Path(args.script_path).read_text(encoding="utf-8")

    command_timeout = config.get("CommandTimeout", 30)

    batches = [
        batch.strip()
        for batch in re.split(r"^\s*GO\s*$", script_text, flags=re.IGNORECASE | re.MULTILINE)
        if batch.strip()
    ]

    total_rows_affected = 0
    for index, batch in enumerate(batches, start=1):
        rows_affected = sql_common.invoke_sql_non_query(connection_string, batch, command_timeout)
        logger.info("Batch %s/%s: %s row(s) affected.", index, len(batches), rows_affected)
        total_rows_affected += rows_affected

    logger.info("Completed %s batch(es), %s row(s) affected total.", len(batches), total_rows_affected)


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "invoke_sql_script_file")

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
