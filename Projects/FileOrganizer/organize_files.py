"""
SYNOPSIS
    Organizes files in a folder into subfolders, either by type (Images,
    Documents, Videos, Audio, Archives, Scripts, Other) or by last-modified
    date (YYYY-MM subfolders). Defaults to a dry run that only PRINTS what
    would happen - pass --apply to actually move files. Only processes files
    directly inside the given folder, not subfolders (so it never recurses
    into folders it already created).

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Adjust CATEGORY_EXTENSIONS to change how file types are grouped

EXAMPLE
    python organize_files.py --path "C:/Users/me/Downloads"
    python organize_files.py --path "C:/Users/me/Downloads" --apply
    python organize_files.py --path "C:/Users/me/Downloads" --by date --apply

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
import shutil
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
LOG_FILE_NAME = LOGS_DIRECTORY / f"organize_files_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]

CATEGORY_EXTENSIONS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".md", ".odt"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Scripts": {".py", ".ps1", ".sh", ".js", ".bat"},
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
    logger = logging.getLogger("organize_files")
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
    parser.add_argument("--path", required=True, help="Folder to organize")
    parser.add_argument("--by", choices=["type", "date"], default="type")
    parser.add_argument("--apply", action="store_true", help="Actually move files. Without this, only prints the plan (dry run).")
    return parser.parse_args()


def category_for_file(file_path):
    extension = file_path.suffix.lower()
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if extension in extensions:
            return category
    return "Other"


def date_folder_for_file(file_path):
    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    return modified_time.strftime("%Y-%m")


def build_plan(folder, by_mode):
    """Returns a list of (source_path, destination_folder_name) for every file
    directly inside `folder` (not recursing into subfolders)."""
    plan = []
    for entry in sorted(folder.iterdir()):
        if not entry.is_file():
            continue
        destination_folder = category_for_file(entry) if by_mode == "type" else date_folder_for_file(entry)
        plan.append((entry, destination_folder))
    return plan


def unique_destination(destination_folder, file_name):
    """Returns a Path inside destination_folder that doesn't already exist,
    appending ' (1)', ' (2)', etc. to the file's stem if there's a collision."""
    candidate = destination_folder / file_name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        candidate = destination_folder / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def main_process(args, logger):
    folder = Path(args.path)
    if not folder.is_dir():
        raise ValueError(f"'{args.path}' is not a valid folder")

    plan = build_plan(folder, args.by)
    if not plan:
        logger.info("No files found directly in %s - nothing to do", folder)
        return

    logger.info("Organizing %s file(s) in %s by %s", len(plan), folder, args.by)
    if not args.apply:
        logger.info("DRY RUN - no files will be moved. Pass --apply to actually move them.")

    moved_count = 0
    for source_path, destination_folder_name in plan:
        destination_folder = folder / destination_folder_name
        if args.apply:
            destination_folder.mkdir(exist_ok=True)
            destination_path = unique_destination(destination_folder, source_path.name)
            shutil.move(str(source_path), str(destination_path))
            logger.info("Moved: %s -> %s", source_path.name, destination_path.relative_to(folder))
            moved_count += 1
        else:
            logger.info("[DRY RUN] Would move: %s -> %s/", source_path.name, destination_folder_name)

    if args.apply:
        logger.info("Moved %s file(s)", moved_count)
    else:
        logger.info("Dry run complete - %s file(s) would be moved. Re-run with --apply to do it.", len(plan))


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
