"""
SYNOPSIS
    Finds exact duplicate files under a folder (recursively) by content
    hash, and reports them grouped together with wasted space. Can also
    delete duplicates (keeping one copy per group) - defaults to a dry run;
    pass --delete to actually remove files, with a confirmation prompt
    unless --yes is also passed.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Adjust --keep if you want a different rule for which copy survives

EXAMPLE
    python find_duplicates.py --path "C:/Users/me/Downloads"
    python find_duplicates.py --path "C:/Users/me/Downloads" --delete
    python find_duplicates.py --path "C:/Users/me/Downloads" --delete --yes

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import hashlib
import importlib
import logging
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
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"find_duplicates_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]
HASH_CHUNK_SIZE = 1024 * 1024  # 1MB chunks, so large files don't need to fully load into memory
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
    logger = logging.getLogger("find_duplicates")
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
    parser.add_argument("--path", required=True, help="Folder to scan (recursively)")
    parser.add_argument("--delete", action="store_true", help="Delete duplicates, keeping one copy per group. Without this, only reports.")
    parser.add_argument("--keep", choices=["first", "oldest", "newest"], default="first",
                         help="Which copy to keep when --delete is used: 'first' (alphabetically), 'oldest', or 'newest' by modified time")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt when --delete is used")
    return parser.parse_args()


def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicate_groups(root, logger):
    """Returns a list of lists of Path - each inner list is a group of files
    with identical content. Groups by size first (cheap), then hashes only
    files that share a size with at least one other file (avoids hashing
    every file when most have unique sizes)."""
    by_size = defaultdict(list)
    file_count = 0
    for file_path in Path(root).rglob("*"):
        if file_path.is_file():
            file_count += 1
            by_size[file_path.stat().st_size].append(file_path)

    logger.info("Scanned %s file(s), %s distinct size(s)", file_count, len(by_size))

    by_hash = defaultdict(list)
    candidates = [group for group in by_size.values() if len(group) > 1]
    hashed_count = sum(len(group) for group in candidates)
    logger.info("Hashing %s file(s) that share a size with at least one other file", hashed_count)

    for group in candidates:
        for file_path in group:
            try:
                file_hash = hash_file(file_path)
                by_hash[file_hash].append(file_path)
            except OSError as ex:
                logger.error("Could not read %s. Details: %s", file_path, ex)

    return [group for group in by_hash.values() if len(group) > 1]


def choose_survivor(group, keep_mode):
    if keep_mode == "first":
        return min(group, key=lambda p: str(p).lower())
    if keep_mode == "oldest":
        return min(group, key=lambda p: p.stat().st_mtime)
    return max(group, key=lambda p: p.stat().st_mtime)  # newest


def main_process(args, logger):
    root = Path(args.path)
    if not root.is_dir():
        raise ValueError(f"'{args.path}' is not a valid folder")

    duplicate_groups = find_duplicate_groups(root, logger)

    if not duplicate_groups:
        logger.info("No duplicates found")
        return

    total_wasted_bytes = 0
    for group in duplicate_groups:
        file_size = group[0].stat().st_size
        wasted = file_size * (len(group) - 1)
        total_wasted_bytes += wasted

        logger.info("--- Duplicate group (%s files, %s bytes each, %s wasted) ---",
                     len(group), file_size, wasted)
        for file_path in sorted(group, key=lambda p: str(p).lower()):
            logger.info("  %s", file_path)

    logger.info("Found %s duplicate group(s), %.2f MB wasted total",
                 len(duplicate_groups), total_wasted_bytes / (1024 * 1024))

    if not args.delete:
        logger.info("Dry run - no files deleted. Re-run with --delete to remove duplicates.")
        return

    if not args.yes:
        answer = input(f"Delete duplicates in {len(duplicate_groups)} group(s), keeping the '{args.keep}' copy of each? [y/N] ")
        if answer.strip().lower() != "y":
            logger.info("Cancelled - no files were deleted")
            return

    deleted_count = 0
    freed_bytes = 0
    for group in duplicate_groups:
        survivor = choose_survivor(group, args.keep)
        for file_path in group:
            if file_path == survivor:
                continue
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                deleted_count += 1
                freed_bytes += file_size
                logger.info("Deleted: %s (kept %s)", file_path, survivor)
            except OSError as ex:
                logger.error("Could not delete %s. Details: %s", file_path, ex)

    logger.info("Deleted %s file(s), freed %.2f MB", deleted_count, freed_bytes / (1024 * 1024))


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
