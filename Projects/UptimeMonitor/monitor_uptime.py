"""
SYNOPSIS
    Checks one or more URLs and reports whether each is up (status < 400) or
    down (status >= 400, or a network error), with response time. Can run a
    single pass (default) or repeated rounds (--count N --interval seconds)
    within one execution, logging state changes (up -> down / down -> up)
    as they happen.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update default args (e.g. --urls) for typical usage
    - For true unattended continuous monitoring, schedule this script to
      run periodically (e.g. Windows Task Scheduler) rather than using a
      very large --count, since a single run still has a finite lifetime.

EXAMPLE
    python monitor_uptime.py --urls https://example.com https://api.github.com
    python monitor_uptime.py --urls-file sites.txt --count 5 --interval 30

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import logging
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = ["requests"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)

import requests
#endregion

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"monitor_uptime_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

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
    logger = logging.getLogger("monitor_uptime")
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
    parser.add_argument("--urls", nargs="+", default=None, help="One or more URLs to check")
    parser.add_argument("--urls-file", default=None, help="Path to a file with one URL per line, instead of --urls")
    parser.add_argument("--count", type=int, default=1, help="Number of check rounds to run")
    parser.add_argument("--interval", type=float, default=60.0, help="Seconds to wait between rounds")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")
    return parser.parse_args()


def load_urls(args):
    if args.urls_file:
        with open(args.urls_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    if args.urls:
        return args.urls
    raise ValueError("Either --urls or --urls-file is required")


def check_url(url, timeout):
    """Returns (is_up, status_code_or_None, response_time_ms, error_or_None)."""
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return response.status_code < 400, response.status_code, elapsed_ms, None
    except requests.exceptions.RequestException as ex:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, None, elapsed_ms, str(ex)


def main_process(args, logger):
    urls = load_urls(args)
    last_status = {}  # url -> True (up) / False (down), across rounds in this run

    for round_number in range(1, args.count + 1):
        logger.info("--- Round %s/%s ---", round_number, args.count)

        for url in urls:
            is_up, status_code, elapsed_ms, error = check_url(url, args.timeout)

            state_word = "UP" if is_up else "DOWN"
            detail = f"status {status_code}" if status_code is not None else f"error: {error}"
            logger.info("%s - %s (%s, %.0fms)", url, state_word, detail, elapsed_ms)

            previous = last_status.get(url)
            if previous is not None and previous != is_up:
                logger.info("!! State change for %s: %s -> %s", url, "UP" if previous else "DOWN", state_word)
            last_status[url] = is_up

        if round_number < args.count:
            time.sleep(args.interval)


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
