"""
SYNOPSIS
    Tests a regex pattern against sample text and shows every match, its
    position, and any numbered/named capture groups.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Add more flag letters to FLAG_MAP if you need them (currently i, m, s, x)

EXAMPLE
    python regex_tester.py --pattern "\\d+" --text "I have 2 cats and 15 dogs"
    python regex_tester.py --pattern "(?P<user>\\w+)@(?P<domain>\\w+\\.\\w+)" --text "contact: ruchik@example.com"
    python regex_tester.py --pattern "^error" --text-file app.log --flags im

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
import re
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # re is standard library

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"regex_tester_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]

FLAG_MAP = {
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
    "x": re.VERBOSE,
}
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
    logger = logging.getLogger("regex_tester")
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
    parser.add_argument("--pattern", required=True, help="Regex pattern to test")
    parser.add_argument("--text", default=None, help="Sample text to test against")
    parser.add_argument("--text-file", default=None, help="Read sample text from this file instead of --text")
    parser.add_argument("--flags", default="", help="Any combination of: i (ignorecase), m (multiline), s (dotall), x (verbose)")
    return parser.parse_args()


def compile_flags(flag_string):
    combined = 0
    for letter in flag_string:
        if letter not in FLAG_MAP:
            raise ValueError(f"Unknown flag '{letter}'. Valid flags: {', '.join(FLAG_MAP)}")
        combined |= FLAG_MAP[letter]
    return combined


def main_process(args, logger):
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text is not None:
        text = args.text
    else:
        raise ValueError("Either --text or --text-file is required")

    flags = compile_flags(args.flags)

    try:
        compiled = re.compile(args.pattern, flags)
    except re.error as ex:
        raise ValueError(f"Invalid regex pattern: {ex}")

    matches = list(compiled.finditer(text))
    logger.info("Pattern: %s", args.pattern)
    logger.info("Flags: %s", args.flags or "(none)")
    logger.info("Found %s match(es)", len(matches))

    if not matches:
        return

    for index, match in enumerate(matches, start=1):
        logger.info("--- Match %s ---", index)
        logger.info("Text: %r (position %s-%s)", match.group(0), match.start(), match.end())

        if match.groups():
            for group_index, group_value in enumerate(match.groups(), start=1):
                logger.info("  Group %s: %r", group_index, group_value)

        if match.groupdict():
            for name, value in match.groupdict().items():
                logger.info("  Named group '%s': %r", name, value)


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
