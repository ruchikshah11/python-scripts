"""
SYNOPSIS
    Gets site or list fields (columns). Equivalent to PnP PowerShell's
    Get-PnPField. Uses the sharepoint library (SharePoint/sharepoint) for the
    SharePoint calls, and the shared sp_logging helper (SharePoint/common)
    for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality
    python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents"
    python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --field-name "Title"
    python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --field-name "Title"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
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
    parser.add_argument("--list-title", default=None, help="Scope to a list's fields; omit for site fields")
    parser.add_argument("--field-name", default=None, help="Internal name or title of one field; omit for all")
    return parser.parse_args()


def main_process(args, logger):
    ctx, _ = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)

    if args.field_name:
        field = sharepoint.get_field(ctx, args.field_name, list_title=args.list_title)
        logger.info("Title: %s", field.properties.get("Title"))
        logger.info("InternalName: %s", field.properties.get("InternalName"))
        logger.info("FieldTypeKind: %s", field.properties.get("FieldTypeKind"))
        logger.info("Required: %s", field.properties.get("Required"))
    else:
        fields = sharepoint.get_fields(ctx, list_title=args.list_title)
        logger.info("Found %s field(s):", len(fields))
        for field in fields:
            logger.info("- %s (InternalName: %s)", field.properties.get("Title"), field.properties.get("InternalName"))


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "get_field")

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
