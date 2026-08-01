"""
SYNOPSIS
    Gets a random quote, general joke, or Chuck Norris joke - no API key
    required. Uses ZenQuotes (quotes), Official Joke API (jokes), and
    api.chucknorris.io (Chuck Norris jokes), all free and keyless.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update default args (e.g. --type, --count) for typical usage

EXAMPLE
    python random_quote.py
    python random_quote.py --type joke
    python random_quote.py --type chuck --count 3

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"random_quote_{datetime.now():%Y%m%d}.log"
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
    logger = logging.getLogger("random_quote")
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
    parser.add_argument("--type", choices=["quote", "joke", "chuck"], default="quote")
    parser.add_argument("--count", type=int, default=1, help="How many to fetch")
    return parser.parse_args()


def get_quote():
    """Returns "text - author" from ZenQuotes."""
    response = requests.get("https://zenquotes.io/api/random", timeout=10)
    response.raise_for_status()
    data = response.json()[0]
    return f'"{data["q"]}" - {data["a"]}'


def get_joke():
    """Returns "setup / punchline" from the Official Joke API."""
    response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=10)
    response.raise_for_status()
    data = response.json()
    return f'{data["setup"]} ... {data["punchline"]}'


def get_chuck_joke():
    """Returns a random Chuck Norris joke from api.chucknorris.io."""
    response = requests.get("https://api.chucknorris.io/jokes/random", timeout=10)
    response.raise_for_status()
    return response.json()["value"]


FETCHERS = {
    "quote": get_quote,
    "joke": get_joke,
    "chuck": get_chuck_joke,
}


def main_process(args, logger):
    fetch = FETCHERS[args.type]
    for i in range(args.count):
        text = fetch()
        logger.info(text)


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
