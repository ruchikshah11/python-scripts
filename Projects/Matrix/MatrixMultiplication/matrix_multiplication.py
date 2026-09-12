"""
SYNOPSIS
    Multiplies two matrices (Matrix A is RowsA x ColsA, Matrix B is RowsB x
    ColsB - not necessarily square, and not necessarily the same size as each
    other, as long as ColsA == RowsB) using the classic triple-loop algorithm,
    and prints Matrix A, Matrix B, and the product.

DESCRIPTION
    By default, prompts for every cell of both matrices one at a time
    (Matrix A first, then Matrix B). Pass --random to generate random
    integers instead (range configurable via --min/--max, reproducible via
    --seed) - useful for a quick demo without typing in every value.

    C[i][j] = sum(A[i][k] * B[k][j] for k in range(ColsA))

    Pure standard library - no numpy - so the algorithm itself is visible
    rather than hidden behind a library call. O(RowsA * ColsB * ColsA) time
    complexity.

EXAMPLE
    python matrix_multiplication.py --rows-a 2 --cols-a 3 --rows-b 3 --cols-b 2
    python matrix_multiplication.py --rows-a 3 --cols-a 3 --rows-b 3 --cols-b 3 --random --seed 42

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"matrix_multiplication_{datetime.now():%Y%m%d}.log"
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
    logger = logging.getLogger("matrix_multiplication")
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


def generate_matrix(rows, cols, min_value, max_value, rng):
    return [[rng.randint(min_value, max_value) for _ in range(cols)] for _ in range(rows)]


def prompt_int(prompt_text):
    while True:
        raw = input(prompt_text)
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def prompt_matrix(name, rows, cols, logger):
    logger.info("Enter values for Matrix %s (%sx%s):", name, rows, cols)
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(prompt_int(f"  {name}[{i + 1}][{j + 1}]: "))
        matrix.append(row)
    return matrix


def multiply_matrices(a, b):
    """C[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_a)) - classic
    O(rows_a * cols_b * cols_a) algorithm. Requires len(a[0]) == len(b)."""
    rows_a, cols_a = len(a), len(a[0])
    cols_b = len(b[0])
    result = [[0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            total = 0
            for k in range(cols_a):
                total += a[i][k] * b[k][j]
            result[i][j] = total
    return result


def format_matrix(matrix):
    width = max(len(str(value)) for row in matrix for value in row)
    lines = []
    for row in matrix:
        lines.append("[ " + "  ".join(str(value).rjust(width) for value in row) + " ]")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Multiply two matrices (RowsA x ColsA) * (RowsB x ColsB).")
    parser.add_argument("--rows-a", type=int, required=True, help="Number of rows in Matrix A")
    parser.add_argument("--cols-a", type=int, required=True, help="Number of columns in Matrix A")
    parser.add_argument("--rows-b", type=int, required=True, help="Number of rows in Matrix B")
    parser.add_argument("--cols-b", type=int, required=True, help="Number of columns in Matrix B")
    parser.add_argument("--random", action="store_true",
                         help="Generate random matrices instead of prompting for values")
    parser.add_argument("--min", type=int, default=1, help="Minimum random value, with --random (default: %(default)s)")
    parser.add_argument("--max", type=int, default=9, help="Maximum random value, with --random (default: %(default)s)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed, with --random, for reproducible matrices")
    return parser.parse_args()


def main_process(args, logger):
    for label, value in (("--rows-a", args.rows_a), ("--cols-a", args.cols_a),
                         ("--rows-b", args.rows_b), ("--cols-b", args.cols_b)):
        if value < 1:
            logger.error("%s must be a positive integer, got %s", label, value)
            sys.exit(1)

    if args.cols_a != args.rows_b:
        logger.error(
            "Cannot multiply a %sx%s matrix by a %sx%s matrix - Matrix A's column count "
            "(%s) must equal Matrix B's row count (%s).",
            args.rows_a, args.cols_a, args.rows_b, args.cols_b, args.cols_a, args.rows_b)
        sys.exit(1)

    if args.random:
        if args.min > args.max:
            logger.error("--min (%s) cannot be greater than --max (%s)", args.min, args.max)
            sys.exit(1)
        rng = random.Random(args.seed)
        matrix_a = generate_matrix(args.rows_a, args.cols_a, args.min, args.max, rng)
        matrix_b = generate_matrix(args.rows_b, args.cols_b, args.min, args.max, rng)
    else:
        matrix_a = prompt_matrix("A", args.rows_a, args.cols_a, logger)
        matrix_b = prompt_matrix("B", args.rows_b, args.cols_b, logger)

    logger.info("Matrix A (%sx%s):\n%s", args.rows_a, args.cols_a, format_matrix(matrix_a))
    logger.info("Matrix B (%sx%s):\n%s", args.rows_b, args.cols_b, format_matrix(matrix_b))

    multiply_start = time.perf_counter()
    result = multiply_matrices(matrix_a, matrix_b)
    multiply_elapsed = time.perf_counter() - multiply_start

    logger.info("Result A x B (%sx%s):\n%s", args.rows_a, args.cols_b, format_matrix(result))
    operations = args.rows_a * args.cols_b * args.cols_a
    logger.info("Multiplication took %.6fs (%s operations)", multiply_elapsed, operations)


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
