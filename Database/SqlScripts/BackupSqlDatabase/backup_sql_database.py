"""
SYNOPSIS
    Backs up the tenant database via BACKUP DATABASE. Uses the sql_common library
    (Database/SqlScripts/common) for the SQL Server calls, and the shared
    db_logging helper (Database/SqlScripts/common) for logging.

DESCRIPTION
    Runs BACKUP DATABASE against the database named in config["ConnectionString"],
    writing a timestamped .bak file into config["BackupDirectory"]. Note that
    BackupDirectory is a path on the SQL Server host itself (not on the machine
    running this script) - SQL Server writes the backup file server-side.
    Python port of Backup-SqlDatabase.ps1.

EXAMPLE
    python backup_sql_database.py
    python backup_sql_database.py --config-path SqlBackupConfig.json

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
    parser.add_argument("--config-path", default=str(SCRIPT_FOLDER / "SqlBackupConfig.json"))
    return parser.parse_args()


def main_process(args, logger):
    config = sql_common.get_sql_script_config(args.config_path)
    database_name = config["Database"]
    connection_string = sql_common.build_connection_string(database_name)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_name = f"{database_name}_{timestamp}.bak"
    backup_directory = config["BackupDirectory"].rstrip("\\")
    backup_path = f"{backup_directory}\\{backup_file_name}"

    query = f"BACKUP DATABASE [{database_name}] TO DISK = N'{backup_path}' WITH INIT, STATS = 10"

    # CommandTimeout 0 = no timeout; backups can run long and shouldn't be cut off.
    sql_common.invoke_sql_non_query(connection_string, query, command_timeout=0)

    logger.info("Backed up %s to %s (path is on the SQL Server host).", database_name, backup_path)


def main():
    args = parse_args()
    logger, correlation_id = db_logging.build_logger(SCRIPT_FOLDER, "backup_sql_database")

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
