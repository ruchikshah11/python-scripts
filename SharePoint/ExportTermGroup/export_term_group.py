"""
SYNOPSIS
    Exports taxonomy term group(s) (term sets + terms) to a JSON file for
    backup/reference - one specific group via --group-name, or every group in
    the term store if omitted. NOT equivalent to PnP PowerShell's
    Export-PnPTermGroupToXml - that produces PnP's own provisioning-template
    XML schema, which no Python library reimplements (see
    SharePoint/sharepoint/README.md). This is a plain JSON snapshot instead -
    not re-importable via PnP or any other tool.

    Uses the sharepoint library (SharePoint/sharepoint) for the SharePoint
    calls, and the shared sp_logging helper (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    # One specific term group
    python export_term_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "MyTermGroup" --output "C:/MyTermGroup.json"

    # Every term group in the term store
    python export_term_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --output "C:/AllTermGroups.json"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
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
    parser.add_argument("--group-name", default=None, help="Name of one term group to export; omit for every group in the term store")
    parser.add_argument("--output", required=True, help="Local path to write the JSON snapshot to")
    return parser.parse_args()


def main_process(args, logger):
    ctx, token_result = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)

    if args.group_name:
        snapshot = sharepoint.export_term_group(ctx, args.group_name, token_result)
        term_set_count = len(snapshot.get("termSets", []))
        logger.info("Exported term group '%s' (%s term set(s))", args.group_name, term_set_count)
    else:
        snapshot = sharepoint.export_term_store(ctx, token_result)
        logger.info("Exported %s term group(s) from the term store", len(snapshot))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    logger.info("Written to %s", args.output)


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "export_term_group")

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
