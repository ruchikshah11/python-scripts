"""
SYNOPSIS
    Updates an existing SharePoint list item by ID. Uses the sharepoint
    library (SharePoint/sharepoint) for the SharePoint calls, and the shared
    sp_logging helper (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python update_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --fields "{\"Title\": \"Renamed\"}"

    # System update - no new version, Modified/Modified By untouched, no workflows triggered
    python update_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --fields "{\"Title\": \"Renamed\"}" --system-update

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.1.0
"""

import argparse
import json
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
    parser.add_argument("--list-title", required=True, help="Title of the list containing the item")
    parser.add_argument("--item-id", required=True, type=int, help="Id of the item to update")
    parser.add_argument("--fields", required=True, help='JSON dict of field values, e.g. \'{"Title": "Renamed"}\'')
    parser.add_argument("--system-update", action="store_true",
                         help="Like Set-PnPListItem -SystemUpdate: no new version, "
                              "Modified/Modified By untouched, no workflows triggered")
    return parser.parse_args()


def main_process(args, logger):
    fields = json.loads(args.fields)

    ctx, _ = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)
    sharepoint.update_list_item(ctx, args.list_title, args.item_id, fields, system_update=args.system_update)

    update_kind = "system update" if args.system_update else "update"
    logger.info("Applied %s to item Id: %s in '%s' with %s", update_kind, args.item_id, args.list_title, fields)


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "update_list_item")

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
