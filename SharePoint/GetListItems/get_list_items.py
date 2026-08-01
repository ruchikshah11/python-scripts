"""
SYNOPSIS
    Connects to a SharePoint site and retrieves items from a specific list.
    Uses the sharepoint library (SharePoint/sharepoint) for the SharePoint calls, and
    the shared sp_logging helper (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python get_list_items.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents"
    python get_list_items.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Tasks" --top 25

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).resolve().parent
SHAREPOINT_FOLDER = SCRIPT_FOLDER.parent
sys.path.insert(0, str(SHAREPOINT_FOLDER))               # for `import sharepoint` (package)
sys.path.insert(0, str(SHAREPOINT_FOLDER / "common"))     # for `import sp_logging`

import sharepoint
import sp_logging

# Same Azure AD app registration Client ID used for interactive auth in your PowerShell scripts.
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"  # or your tenant domain, e.g. "bsonedev.onmicrosoft.com"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", default="https://bsonedev.sharepoint.com/sites/bsonequality")
    parser.add_argument("--list-title", required=True, help="Title of the list to read items from")
    parser.add_argument("--top", type=int, default=10, help="Max number of items to retrieve")
    return parser.parse_args()


def main_process(args, logger):
    ctx, _ = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)

    items = sharepoint.get_list_items(ctx, args.list_title, top=args.top)

    logger.info("Retrieved %s item(s) from '%s'", len(items), args.list_title)
    for item in items:
        logger.info(
            "Id: %s | Title: %s | Modified: %s",
            item.properties.get("ID"),
            item.properties.get("Title"),
            item.properties.get("Modified"),
        )


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "get_list_items")

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, correlation_id)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, correlation_id)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, correlation_id, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
