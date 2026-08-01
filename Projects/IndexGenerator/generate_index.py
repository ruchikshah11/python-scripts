"""
SYNOPSIS
    Regenerates INDEX.md by scanning the repo for .py scripts and reading
    each one's own docstring, so the index can no longer drift from reality
    via hand-editing. Mirrors the format/logic of the PowerShell repo's
    Update-ScriptIndex.ps1 (C:/Ruchik/PowerShell/Utilities/DevTooling/
    Update-ScriptIndex/Update-ScriptIndex.ps1), adapted for Python docstrings.

DESCRIPTION
    Walks every .py file under the repo root, grouping entries by top-level
    folder (category) and, where a script sits two or more folders deep,
    its immediate child folder (subcategory heading). Scripts that sit
    directly one level under the category root (Category/file.py) are
    listed flat, without a subheading.

    For each script, a one-line description is pulled from its own module
    docstring's SYNOPSIS section (via `ast`, so nothing is ever executed),
    falling back to the docstring's first paragraph, or left blank if there's
    no docstring at all. Categories are sorted by script count (descending);
    scripts within a section are sorted case-insensitive ordinal by filename.

    Re-run this script any time you add or change scripts to keep INDEX.md
    up to date - it's generated output, not meant to be hand-edited.

EXAMPLE
    python generate_index.py
    python generate_index.py --root "C:/Users/ruchik.shah/Downloads/Python"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-01
    Modified by : Ruchik Shah
    Modified on : 2026-08-01
    Version     : 2.0.0
"""

import argparse
import ast
import importlib
import logging
import re
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # ast, re, pathlib are all standard library

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"generate_index_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]
EXCLUDED_DIR_NAMES = {"__pycache__", "Logs", ".venv", "venv", "env", ".git"}
MAX_DESCRIPTION_LENGTH = 300

SYNOPSIS_RE = re.compile(r"SYNOPSIS\s*\n(.*?)(?:\n\s*\n\s*[A-Z]+\s*\n|\Z)", re.DOTALL)
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
    logger = logging.getLogger("generate_index")
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
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root folder to scan for .py files")
    parser.add_argument("--output", default=None, help="Defaults to INDEX.md inside --root")
    return parser.parse_args()


def find_python_files(root):
    """Returns every *.py file under root, recursively, skipping EXCLUDED_DIR_NAMES
    and this script itself."""
    root_path = Path(root)
    this_file = Path(__file__).resolve()
    results = []

    for path in sorted(root_path.rglob("*.py")):
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        if path.resolve() == this_file:
            continue
        results.append(path)

    return results


def clean_text(text):
    """Collapses whitespace, strips leading punctuation/whitespace, and
    truncates to MAX_DESCRIPTION_LENGTH with a trailing '...' if needed -
    same rules as the PowerShell generator's ConvertTo-CleanText."""
    if not text:
        return ""
    cleaned = " ".join(text.split())
    cleaned = cleaned.lstrip(". \t")
    if len(cleaned) > MAX_DESCRIPTION_LENGTH:
        cleaned = cleaned[:MAX_DESCRIPTION_LENGTH - 3] + "..."
    return cleaned


def extract_description(file_path):
    """Returns a one-line description extracted from the module's own
    docstring (via `ast`, so nothing is ever executed): the SYNOPSIS section
    if present, else the docstring's first paragraph, else "" if there's no
    docstring at all - left blank rather than guessing, same as the
    PowerShell generator."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
        docstring = ast.get_docstring(tree)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return ""

    if not docstring:
        return ""

    match = SYNOPSIS_RE.search(docstring)
    block = match.group(1) if match else docstring.split("\n\n")[0]
    return clean_text(block)


def encode_url_path(relative_path):
    """Percent-encodes spaces and parentheses in each path segment, joined
    with '/' - matches the PowerShell generator's ConvertTo-LinkUrl."""
    segments = relative_path.as_posix().split("/")
    encoded = [segment.replace(" ", "%20").replace("(", "%28").replace(")", "%29") for segment in segments]
    return "/".join(encoded)


def build_entries(root, logger):
    """Returns a list of dicts: {category, heading, name, rel_path, desc}."""
    root_path = Path(root)
    files = find_python_files(root_path)
    logger.info("Found %s Python file(s) under %s", len(files), root_path)

    entries = []
    for file_path in files:
        relative = file_path.relative_to(root_path)
        parts = relative.parts
        category = parts[0]
        heading = parts[1] if len(parts) >= 3 else ""

        entries.append({
            "category": category,
            "heading": heading,
            "name": file_path.name,
            "rel_path": relative,
            "desc": extract_description(file_path),
        })

    missing = sum(1 for entry in entries if not entry["desc"])
    if missing:
        logger.info("%s file(s) had no usable description", missing)

    return entries


def make_anchor(name):
    anchor = re.sub(r"[^a-z0-9\- ]", "", name.lower())
    return anchor.replace(" ", "-")


def render_entry_line(entry):
    url = encode_url_path(entry["rel_path"])
    line = f"- [`{entry['name']}`]({url})"
    if entry["desc"]:
        line += f" \u2014 {entry['desc']}"
    return line


def render_markdown(entries):
    by_category = defaultdict(list)
    for entry in entries:
        by_category[entry["category"]].append(entry)

    # Categories sorted by count descending, ties broken alphabetically (ordinal, case-insensitive)
    category_order = sorted(by_category, key=lambda name: name.lower())
    category_order.sort(key=lambda name: len(by_category[name]), reverse=True)

    lines = [
        "# Python Script Index",
        "",
        "Auto-generated index of every script under this repo, grouped by category and subfolder.",
        "Regenerated by [Projects/IndexGenerator/generate_index.py](Projects/IndexGenerator/generate_index.py) "
        "- do not hand-edit this file; re-run that script instead.",
        "",
        f"**{len(entries)} scripts across {len(category_order)} categories**",
        "",
        "## Contents",
        "",
    ]

    for category in category_order:
        count = len(by_category[category])
        lines.append(f"- [{category} ({count})](#{make_anchor(category)})")

    lines.append("")
    lines.append("---")

    for category in category_order:
        lines.append("")
        lines.append(f"## {category}")

        category_entries = by_category[category]
        flat_entries = sorted((e for e in category_entries if not e["heading"]), key=lambda e: e["name"].lower())
        if flat_entries:
            lines.append("")
            for entry in flat_entries:
                lines.append(render_entry_line(entry))

        heading_groups = defaultdict(list)
        for entry in category_entries:
            if entry["heading"]:
                heading_groups[entry["heading"]].append(entry)

        for heading in sorted(heading_groups, key=lambda name: name.lower()):
            lines.append("")
            lines.append(f"### {heading}")
            lines.append("")
            for entry in sorted(heading_groups[heading], key=lambda e: e["name"].lower()):
                lines.append(render_entry_line(entry))

    lines.append("")
    return "\n".join(lines)


def main_process(args, logger):
    entries = build_entries(args.root, logger)
    markdown = render_markdown(entries)

    output_path = Path(args.output) if args.output else Path(args.root) / "INDEX.md"
    output_path.write_text(markdown, encoding="utf-8")

    categories = {entry["category"] for entry in entries}
    logger.info("Wrote index of %s script(s) across %s categories to %s",
                 len(entries), len(categories), output_path)


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
