"""
SYNOPSIS
    Converts an amount between currencies using the free Frankfurter API
    (European Central Bank reference rates) - no API key required. Can also
    list every supported currency code. Provides logging (with daily log
    rotation, retention, and per-run CorrelationID), module dependency
    checking, and error handling.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update default args (e.g. --from-currency, --to-currency) for typical usage

EXAMPLE
    python convert_currency.py --amount 100 --from-currency USD --to-currency EUR
    python convert_currency.py --list-currencies

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"convert_currency_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

BASE_URL = "https://api.frankfurter.app"
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
    logger = logging.getLogger("convert_currency")
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
    parser.add_argument("--amount", type=float, default=1.0)
    parser.add_argument("--from-currency", default="USD", help="3-letter currency code, e.g. USD")
    parser.add_argument("--to-currency", default="EUR", help="3-letter currency code, e.g. EUR")
    parser.add_argument("--list-currencies", action="store_true", help="List every supported currency code and exit")
    return parser.parse_args()


def get_supported_currencies(logger):
    """Returns a dict of {code: full_name} for every currency Frankfurter supports."""
    logger.info("Fetching supported currencies")
    response = requests.get(f"{BASE_URL}/currencies")
    response.raise_for_status()
    return response.json()


def convert_currency(amount, from_currency, to_currency, logger):
    """Returns Frankfurter's conversion response: {"amount":.., "base":.., "date":.., "rates": {to_currency: value}}.
    Raises ValueError with a friendly message for bad currency codes/pairs."""
    logger.info("Converting %s %s to %s", amount, from_currency, to_currency)
    params = {"amount": amount, "from": from_currency, "to": to_currency}
    response = requests.get(f"{BASE_URL}/latest", params=params)

    if not response.ok:
        detail = response.json().get("message", response.text)
        raise ValueError(f"Conversion failed ({response.status_code}): {detail}")

    return response.json()


def main_process(args, logger):
    if args.list_currencies:
        currencies = get_supported_currencies(logger)
        logger.info("Supported currencies (%s):", len(currencies))
        for code, name in sorted(currencies.items()):
            logger.info("%s - %s", code, name)
        return

    from_currency = args.from_currency.upper()
    to_currency = args.to_currency.upper()

    if from_currency == to_currency:
        # Frankfurter's API rejects same-currency pairs (422 "bad currency pair") -
        # handle it directly instead of calling the API for a trivial 1:1 conversion.
        logger.info("%s %s = %s %s (same currency, rate 1.0)", args.amount, from_currency, args.amount, to_currency)
        return

    result = convert_currency(args.amount, from_currency, to_currency, logger)
    converted = result["rates"][to_currency]
    rate = converted / args.amount if args.amount else 0

    logger.info("Date: %s", result["date"])
    logger.info("%s %s = %s %s", args.amount, from_currency, converted, to_currency)
    logger.info("Rate: 1 %s = %s %s", from_currency, round(rate, 6), to_currency)


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
