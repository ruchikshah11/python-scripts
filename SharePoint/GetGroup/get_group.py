"""
SYNOPSIS
    Gets SharePoint groups, an associated Owner/Member/Visitor group, or a
    group's members. Equivalent to PnP PowerShell's Get-PnPGroup /
    Get-PnPGroupMembers. Uses the sharepoint library (SharePoint/sharepoint)
    for the SharePoint calls, and the shared sp_logging helper
    (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality
    python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "Members"
    python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --associated member
    python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "Members" --members

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
    parser.add_argument("--group-name", default=None, help="Name of one group; omit (with no --associated) for all")
    parser.add_argument("--associated", choices=["owner", "member", "visitor"], default=None,
                         help="Get the site's associated Owner/Member/Visitor group instead of by name")
    parser.add_argument("--members", action="store_true", help="Show the resolved group's members instead of its details")
    return parser.parse_args()


def main_process(args, logger):
    ctx, _ = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)

    if args.associated:
        group = sharepoint.get_associated_group(ctx, args.associated)
    elif args.group_name:
        group = sharepoint.get_group(ctx, args.group_name)
    else:
        if args.members:
            logger.error("Pass --group-name or --associated to identify which group's members to show")
            return
        groups = sharepoint.get_groups(ctx)
        logger.info("Found %s group(s):", len(groups))
        for group in groups:
            logger.info("- %s", group.properties.get("Title"))
        return

    if args.members:
        members = sharepoint.get_group_members(ctx, group.properties.get("Title"))
        logger.info("Found %s member(s) of '%s':", len(members), group.properties.get("Title"))
        for member in members:
            logger.info("- %s (%s)", member.properties.get("Title"), member.properties.get("Email"))
    else:
        logger.info("Title: %s", group.properties.get("Title"))
        logger.info("Id: %s", group.properties.get("Id"))
        logger.info("OwnerTitle: %s", group.properties.get("OwnerTitle"))


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "get_group")

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
