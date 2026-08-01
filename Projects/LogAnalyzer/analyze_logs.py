"""
SYNOPSIS
    Scans every Logs/ folder under a project root (recursively) and
    summarizes runs, successes, failures, durations, and error counts per
    script - across all the scripts in this workspace that use the shared
    daily-log-file/CorrelationID logging pattern. Provides logging (with
    daily log rotation, retention, and per-run CorrelationID) for its own
    operation, module dependency checking, and error handling.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update DEFAULT_ROOT if your scripts live somewhere else
    - Adjust the regex patterns if your logging format differs

EXAMPLE
    python analyze_logs.py
    python analyze_logs.py --root "C:/Users/ruchik.shah/Downloads/Python"
    python analyze_logs.py --output summary.json

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import json
import logging
import re
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # only standard library modules used

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPT_FOLDER.parent.parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"analyze_logs_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]

# Matches lines written by the shared logging pattern:
#     "%(asctime)s %(levelname)s\t%(message)s"  with datefmt "%Y-%m-%d %H:%M:%S"
LINE_RE = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+)\t(?P<message>.*)$")
# Log file names follow "<script_name>_<yyyyMMdd>.log"
FILE_NAME_RE = re.compile(r"^(?P<script>.+)_\d{8}\.log$")

START_RE = re.compile(r"^Script started at")
FINISH_RE = re.compile(r"^Script finished at .*time taken: (?P<seconds>[\d.]+)s")
FAIL_RE = re.compile(r"^Script failed at .*time taken: (?P<seconds>[\d.]+)s.*Details: (?P<details>.+)$")
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
    logger = logging.getLogger("analyze_logs")
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
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root folder to scan for Logs/ subfolders")
    parser.add_argument("--output", default=None, help="Optional path to save the summary as JSON")
    return parser.parse_args()


def find_log_files(root):
    """Returns every *.log file inside any Logs/ folder under root, recursively."""
    return sorted(Path(root).glob("**/Logs/*.log"))


def script_name_from_file(log_file):
    match = FILE_NAME_RE.match(log_file.name)
    return match.group("script") if match else log_file.stem


def new_stat_entry():
    return {
        "runs": 0,
        "successes": 0,
        "failures": 0,
        "error_lines": 0,
        "durations": [],
        "last_run": None,
        "last_failure_details": None,
        "log_files": set(),
    }


def analyze(log_files):
    """Returns {script_name: stat_entry} aggregated across every given log file."""
    stats = defaultdict(new_stat_entry)

    for log_file in log_files:
        script_name = script_name_from_file(log_file)
        entry = stats[script_name]
        entry["log_files"].add(str(log_file))

        with open(log_file, "r", encoding="utf-8") as f:
            for raw_line in f:
                match = LINE_RE.match(raw_line.rstrip("\n"))
                if not match:
                    continue

                level = match.group("level")
                message = match.group("message")

                if level == "ERROR":
                    entry["error_lines"] += 1

                if START_RE.match(message):
                    entry["runs"] += 1
                    try:
                        ts = datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S")
                        if entry["last_run"] is None or ts > entry["last_run"]:
                            entry["last_run"] = ts
                    except ValueError:
                        pass
                    continue

                finish_match = FINISH_RE.match(message)
                if finish_match:
                    entry["successes"] += 1
                    entry["durations"].append(float(finish_match.group("seconds")))
                    continue

                fail_match = FAIL_RE.match(message)
                if fail_match:
                    entry["failures"] += 1
                    entry["durations"].append(float(fail_match.group("seconds")))
                    entry["last_failure_details"] = fail_match.group("details")

    return stats


def print_summary(stats):
    if not stats:
        print("No log files found.")
        return

    total_runs = sum(entry["runs"] for entry in stats.values())
    total_failures = sum(entry["failures"] for entry in stats.values())
    total_errors = sum(entry["error_lines"] for entry in stats.values())

    print(f"Scripts analyzed: {len(stats)}")
    print(f"Total runs: {total_runs} | Total failures: {total_failures} | Total ERROR lines: {total_errors}")

    for script_name in sorted(stats):
        entry = stats[script_name]
        durations = entry["durations"]

        print(f"\n--- {script_name} ---")
        print(f"Runs: {entry['runs']} | Successes: {entry['successes']} | "
              f"Failures: {entry['failures']} | Error lines: {entry['error_lines']}")
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"Duration (s): avg {avg_duration:.3f}, min {min(durations):.3f}, max {max(durations):.3f}")
        if entry["last_run"]:
            print(f"Last run: {entry['last_run']}")
        if entry["last_failure_details"]:
            print(f"Last failure: {entry['last_failure_details']}")


def stats_to_json_safe(stats):
    result = {}
    for script_name, entry in stats.items():
        durations = entry["durations"]
        result[script_name] = {
            "runs": entry["runs"],
            "successes": entry["successes"],
            "failures": entry["failures"],
            "error_lines": entry["error_lines"],
            "avg_duration_seconds": (sum(durations) / len(durations)) if durations else None,
            "min_duration_seconds": min(durations) if durations else None,
            "max_duration_seconds": max(durations) if durations else None,
            "last_run": entry["last_run"].isoformat() if entry["last_run"] else None,
            "last_failure_details": entry["last_failure_details"],
            "log_files": sorted(entry["log_files"]),
        }
    return result


def main_process(args, logger):
    log_files = find_log_files(args.root)
    logger.info("Found %s log file(s) under %s", len(log_files), args.root)

    stats = analyze(log_files)
    print_summary(stats)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(stats_to_json_safe(stats), f, indent=2)
        logger.info("Summary written to %s", args.output)


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
