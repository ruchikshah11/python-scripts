"""
Shared logging helper. Import this from any script under Database/SqlScripts/
instead of duplicating the daily-log-file / retention / CorrelationID boilerplate.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PURGE_LOG_DAYS = 7


def build_logger(script_folder, script_name):
    """Sets up a logger writing to <script_folder>/Logs/<script_name>_<date>.log,
    purges log files older than PURGE_LOG_DAYS, and returns (logger, correlation_id)."""
    logs_directory = Path(script_folder) / "Logs"
    logs_directory.mkdir(parents=True, exist_ok=True)

    log_file_name = logs_directory / f"{script_name}_{datetime.now():%Y%m%d}.log"
    correlation_id = str(uuid.uuid4())[:11]

    logger = logging.getLogger(script_name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _delete_old_logs(logger, logs_directory)

    return logger, correlation_id


def _delete_old_logs(logger, logs_directory):
    if PURGE_LOG_DAYS <= 0:
        return
    try:
        logger.info("Deleting log files older than %s days", PURGE_LOG_DAYS)
        cutoff = datetime.now() - timedelta(days=PURGE_LOG_DAYS)
        for log_file in logs_directory.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
        logger.info("Log files deleted")
    except Exception as ex:
        logger.error("Error deleting log files. Details: %s", ex)
