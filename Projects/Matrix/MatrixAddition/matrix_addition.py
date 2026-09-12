"""
SYNOPSIS
    Adds two Rows x Cols matrices (both matrices must be - and are - the same
    shape, since addition requires identical dimensions) and prints Matrix A,
    Matrix B, and the sum.

DESCRIPTION
    Prompts for the matrix size (Rows, then Cols) if --rows/--cols aren't
    passed on the command line. Then, by default, prompts for every cell of
    both matrices one at a time (Matrix A first, then Matrix B). Pass
    --random to generate random integers instead (range configurable via
    --min/--max, reproducible via --seed) - useful for a quick demo without
    typing in every value.

    C[i][j] = A[i][j] + B[i][j]

    Pure standard library. O(Rows * Cols) time complexity.

EXAMPLE
    python matrix_addition.py
    python matrix_addition.py --rows 2 --cols 3
    python matrix_addition.py --rows 3 --cols 3 --random --seed 42

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-09-07
    Modified by :
    Modified on :
    Version     : 2.0.0
"""

import argparse
import logging
import random
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"matrix_addition_{datetime.now():%Y%m%d}.log"
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
    logger = logging.getLogger("matrix_addition")
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


def prompt_int(prompt_text):
    while True:
        raw = input(prompt_text)
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def prompt_positive_int(prompt_text):
    while True:
        value = prompt_int(prompt_text)
        if value >= 1:
            return value
        print("Please enter a positive whole number.")


def generate_matrix(rows, cols, min_value, max_value, rng):
    return [[rng.randint(min_value, max_value) for _ in range(cols)] for _ in range(rows)]


def prompt_matrix(name, rows, cols, logger):
    logger.info("Enter values for Matrix %s (%sx%s):", name, rows, cols)
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(prompt_int(f"  {name}[{i + 1}][{j + 1}]: "))
        matrix.append(row)
    return matrix


def add_matrices(a, b):
    """C[i][j] = A[i][j] + B[i][j] - requires identical dimensions."""
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def format_matrix(matrix):
    width = max(len(str(value)) for row in matrix for value in row)
    lines = []
    for row in matrix:
        lines.append("[ " + "  ".join(str(value).rjust(width) for value in row) + " ]")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Add two Rows x Cols matrices.")
    parser.add_argument("--rows", type=int, default=None, help="Number of rows in both matrices (prompted for if omitted)")
    parser.add_argument("--cols", type=int, default=None, help="Number of columns in both matrices (prompted for if omitted)")
    parser.add_argument("--random", action="store_true",
                         help="Generate random matrices instead of prompting for values")
    parser.add_argument("--min", type=int, default=1, help="Minimum random value, with --random (default: %(default)s)")
    parser.add_argument("--max", type=int, default=9, help="Maximum random value, with --random (default: %(default)s)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed, with --random, for reproducible matrices")
    return parser.parse_args()


def main_process(args, logger):
    rows = args.rows if args.rows is not None else prompt_positive_int("Enter number of rows: ")
    cols = args.cols if args.cols is not None else prompt_positive_int("Enter number of columns: ")

    if rows < 1:
        logger.error("--rows must be a positive integer, got %s", rows)
        sys.exit(1)
    if cols < 1:
        logger.error("--cols must be a positive integer, got %s", cols)
        sys.exit(1)

    if args.random:
        if args.min > args.max:
            logger.error("--min (%s) cannot be greater than --max (%s)", args.min, args.max)
            sys.exit(1)
        rng = random.Random(args.seed)
        matrix_a = generate_matrix(rows, cols, args.min, args.max, rng)
        matrix_b = generate_matrix(rows, cols, args.min, args.max, rng)
    else:
        matrix_a = prompt_matrix("A", rows, cols, logger)
        matrix_b = prompt_matrix("B", rows, cols, logger)

    logger.info("Matrix A (%sx%s):\n%s", rows, cols, format_matrix(matrix_a))
    logger.info("Matrix B (%sx%s):\n%s", rows, cols, format_matrix(matrix_b))

    add_start = time.perf_counter()
    result = add_matrices(matrix_a, matrix_b)
    add_elapsed = time.perf_counter() - add_start

    logger.info("Result A + B (%sx%s):\n%s", rows, cols, format_matrix(result))
    operations = rows * cols
    logger.info("Addition took %.6fs (%s operations)", add_elapsed, operations)


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
