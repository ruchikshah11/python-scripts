"""
SYNOPSIS
    Generic, config-driven text editor: inserts a snippet of text on its own
    line, immediately before the first line containing a given marker string,
    in each of a list of files - e.g. adding a new <p> paragraph before the
    closing "Thank You"/"Vielen Dank" line of several email-template HTML
    files in one run, without hand-editing each file or writing a one-off
    script per change.

    This is the Python port of the PowerShell version
    (C:/Ruchik/powershell-scripts/SharePoint/Provisioning/Templates/
    Add-HtmlSnippetBeforeMarker/Add-HtmlSnippetBeforeMarker.ps1) - keep both
    in sync if the config shape or matching/insertion rules change.

DESCRIPTION
    Not specific to email templates or HTML - works on any text file. Every
    edit is described in the JSON config as one {file_path, marker, snippet}
    object in an "edits" array, so the same shape scales to 1 file or 100:
        - file_path : the file to edit (absolute path).
        - marker    : a literal substring - the first line CONTAINING it is
                      where the snippet gets inserted, immediately before
                      that line.
        - snippet   : the literal text to insert as a new line of its own.

    For each edit:
    - IDEMPOTENT: if snippet already appears anywhere in the file, it's
      treated as already applied and skipped - safe to re-run the same
      config repeatedly (e.g. after merging branches) without duplicating
      the insertion.
    - The new line is indented to match whatever leading whitespace the
      marker's own line has - no hard-coded indent width, so it fits
      whatever style the surrounding file already uses.
    - The file's own line-ending style (CRLF vs LF - detected from the file
      itself, not assumed) is preserved for the new line too, so a CRLF file
      stays all-CRLF and an LF file stays all-LF; nothing else in the file is
      touched.
    - A marker that doesn't match any line in the file is reported and
      skipped - never partially applied or guessed at.

EXAMPLE
    python insert_html_snippet_before_marker.py --dry-run
    python insert_html_snippet_before_marker.py
    python insert_html_snippet_before_marker.py --config-path "C:/some/other-config.json"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-09-10
    Modified by :
    Modified on :
    Version     : 1.0.0

    Config file shape (insert_html_snippet_before_marker.json, alongside this
    script by default):
    {
      "dry_run": false,
      "edits": [
        {
          "file_path": "C:\\path\\to\\SomeTemplateEN.html",
          "marker": "<p>Thank You</p>",
          "snippet": "<p><b>[ApproverComments]</b></p>"
        }
      ]
    }
    dry_run defaults to false (a real run) if set in neither place - the
    --dry-run flag on the command line always wins over the config's
    "dry_run" when both are present. "edits" is required and must have at
    least one entry, each requiring all three of file_path/marker/snippet.
"""

import argparse
import json
import logging
import re
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"insert_html_snippet_before_marker_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

DEFAULT_CONFIG_PATH = SCRIPT_FOLDER / "insert_html_snippet_before_marker.json"

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
    logger = logging.getLogger("insert_html_snippet_before_marker")
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


def load_config(config_path, dry_run_flag_passed, dry_run_flag_value, logger):
    """Reads the JSON config and returns (edits, dry_run). dry_run_flag_value
    (the --dry-run switch) always wins over the config's own "dry_run" key
    when the flag was actually passed on the command line."""
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", path)
        sys.exit(1)

    config = json.loads(path.read_text(encoding="utf-8"))

    edits = config.get("edits") or []
    if not edits:
        logger.error("Config file '%s' has no 'edits' entries", path)
        sys.exit(1)

    for i, edit in enumerate(edits):
        for required in ("file_path", "marker", "snippet"):
            if not edit.get(required):
                logger.error("Config file '%s': edits[%d] is missing required value '%s'", path, i, required)
                sys.exit(1)

    dry_run = dry_run_flag_value if dry_run_flag_passed else bool(config.get("dry_run", False))

    logger.info(
        "Loaded config from '%s': %d edit(s), dry_run=%s (%s)",
        path, len(edits), dry_run, "from --dry-run" if dry_run_flag_passed else "from config",
    )
    return edits, dry_run


def get_dominant_newline(text):
    """Returns "\\r\\n" or "\\n" depending on which the file predominantly
    uses - so a newly inserted line matches the file's own convention instead
    of assuming one. Defaults to "\\r\\n" for an empty/newline-free file (the
    common Windows case)."""
    total_lf = text.count("\n")
    if total_lf == 0:
        return "\r\n"
    crlf_count = text.count("\r\n")
    return "\r\n" if crlf_count == total_lf else "\n"


def apply_edit(edit, dry_run, logger):
    """Returns one of "inserted", "already_present", "marker_not_found",
    "file_not_found"."""
    file_path = Path(edit["file_path"])
    marker = edit["marker"]
    snippet = edit["snippet"]

    if not file_path.exists():
        logger.warning("'%s': file not found - skipped", file_path)
        return "file_not_found"

    # newline="" disables Python's universal-newline translation, which would
    # otherwise silently rewrite every "\r\n" to "\n" on read (and vice versa
    # on write) - exactly the class of bug that hit the PowerShell version of
    # this script (there: two variables colliding under case-insensitivity
    # instead of an implicit newline translation, same symptom either way:
    # the file's real line-ending convention silently getting lost).
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        content = f.read()

    if snippet in content:
        return "already_present"

    line_ending = get_dominant_newline(content)
    lines = re.split(r"\r\n|\n", content)

    marker_line_index = next((i for i, line in enumerate(lines) if marker in line), None)
    if marker_line_index is None:
        logger.warning("'%s': marker '%s' not found - skipped", file_path, marker)
        return "marker_not_found"

    leading_whitespace = re.match(r"^\s*", lines[marker_line_index]).group()
    inserted_line = leading_whitespace + snippet

    updated_lines = []
    for i, line in enumerate(lines):
        if i == marker_line_index:
            updated_lines.append(inserted_line)
        updated_lines.append(line)
    new_content = line_ending.join(updated_lines)

    logger.info(
        "%s '%s' before '%s' in '%s'",
        "Would insert" if dry_run else "Inserting", snippet, marker, file_path,
    )
    if not dry_run:
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_content)
    return "inserted"


def main_process(config_path, dry_run_flag_passed, dry_run_flag_value, logger):
    edits, dry_run = load_config(config_path, dry_run_flag_passed, dry_run_flag_value, logger)

    counts = {"inserted": 0, "already_present": 0, "marker_not_found": 0, "file_not_found": 0}
    for edit in edits:
        counts[apply_edit(edit, dry_run, logger)] += 1

    logger.info(
        "Summary: %d edit(s) - %d %s inserted, %d already present (no change needed), "
        "%d skipped (marker not found), %d skipped (file not found)",
        len(edits), counts["inserted"], "would be" if dry_run else "were",
        counts["already_present"], counts["marker_not_found"], counts["file_not_found"],
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Insert a text snippet before the first line matching a marker, across a config-driven list of files."
    )
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH),
                         help="Path to the JSON config (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true", default=None,
                         help="Preview only - logs what would change, writes nothing. Always wins over the config's own \"dry_run\" when passed.")
    return parser.parse_args()


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

        dry_run_flag_passed = args.dry_run is not None
        main_process(args.config_path, dry_run_flag_passed, bool(args.dry_run), logger)

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
