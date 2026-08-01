"""
SYNOPSIS
    Converts a value between units of length, weight, or temperature.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Add more units to LENGTH_TO_METERS / WEIGHT_TO_GRAMS if needed

EXAMPLE
    python convert_units.py --category length --value 5 --from-unit mi --to-unit km
    python convert_units.py --category weight --value 1 --from-unit kg --to-unit lb
    python convert_units.py --category temperature --value 100 --from-unit C --to-unit F
    python convert_units.py --category length --list-units

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
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"convert_units_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]

# Linear categories: unit -> factor to convert 1 of that unit into the base unit
LENGTH_TO_METERS = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}
WEIGHT_TO_GRAMS = {
    "mg": 0.001, "g": 1.0, "kg": 1000.0,
    "oz": 28.349523125, "lb": 453.59237,
}
TEMPERATURE_UNITS = ["C", "F", "K"]
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
    logger = logging.getLogger("convert_units")
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
    parser.add_argument("--category", required=True, choices=["length", "weight", "temperature"])
    parser.add_argument("--value", type=float, default=None)
    parser.add_argument("--from-unit", default=None)
    parser.add_argument("--to-unit", default=None)
    parser.add_argument("--list-units", action="store_true", help="List valid units for --category and exit")
    return parser.parse_args()


def convert_linear(value, from_unit, to_unit, table):
    if from_unit not in table:
        raise ValueError(f"Unknown unit '{from_unit}'. Valid units: {', '.join(table)}")
    if to_unit not in table:
        raise ValueError(f"Unknown unit '{to_unit}'. Valid units: {', '.join(table)}")
    base_value = value * table[from_unit]
    return base_value / table[to_unit]


def convert_temperature(value, from_unit, to_unit):
    if from_unit not in TEMPERATURE_UNITS:
        raise ValueError(f"Unknown unit '{from_unit}'. Valid units: {', '.join(TEMPERATURE_UNITS)}")
    if to_unit not in TEMPERATURE_UNITS:
        raise ValueError(f"Unknown unit '{to_unit}'. Valid units: {', '.join(TEMPERATURE_UNITS)}")

    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    else:  # K
        celsius = value - 273.15

    if to_unit == "C":
        return celsius
    elif to_unit == "F":
        return celsius * 9 / 5 + 32
    else:  # K
        return celsius + 273.15


def main_process(args, logger):
    if args.list_units:
        if args.category == "length":
            logger.info("Length units: %s", ", ".join(LENGTH_TO_METERS))
        elif args.category == "weight":
            logger.info("Weight units: %s", ", ".join(WEIGHT_TO_GRAMS))
        else:
            logger.info("Temperature units: %s", ", ".join(TEMPERATURE_UNITS))
        return

    if args.value is None or not args.from_unit or not args.to_unit:
        raise ValueError("--value, --from-unit, and --to-unit are required unless --list-units is passed")

    if args.category == "length":
        result = convert_linear(args.value, args.from_unit, args.to_unit, LENGTH_TO_METERS)
    elif args.category == "weight":
        result = convert_linear(args.value, args.from_unit, args.to_unit, WEIGHT_TO_GRAMS)
    else:
        result = convert_temperature(args.value, args.from_unit, args.to_unit)

    logger.info("%s %s = %s %s", args.value, args.from_unit, round(result, 6), args.to_unit)


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
