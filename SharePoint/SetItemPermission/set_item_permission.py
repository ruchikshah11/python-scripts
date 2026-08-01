"""
SYNOPSIS
    Manages a list item's permissions: break/reset inheritance, view current
    role assignments, or add/remove a role for a principal. Equivalent to
    PnP PowerShell's Get-PnPListItemPermission / Set-PnPListItemPermission.
    Destructive for break/reset/add-role/remove-role - prompts for
    confirmation unless --yes is passed. Uses the sharepoint library
    (SharePoint/sharepoint) for the SharePoint calls, and the shared
    sp_logging helper (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action get
    python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action break
    python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action reset
    python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action add-role --principal "user@contoso.com" --role "Read"
    python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action remove-role --principal "user@contoso.com" --role "Read"

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

DESTRUCTIVE_ACTIONS = ("break", "reset", "add-role", "remove-role")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", default="https://bsonedev.sharepoint.com/sites/bsonequality")
    parser.add_argument("--list-title", required=True, help="Title of the list containing the item")
    parser.add_argument("--item-id", required=True, type=int, help="Id of the item")
    parser.add_argument("--action", required=True, choices=["get", "break", "reset", "add-role", "remove-role"])
    parser.add_argument("--principal", default=None, help="User login name or group name (required for add-role/remove-role)")
    parser.add_argument("--role", default=None, help='Role name, e.g. "Read", "Contribute", "Full Control" (required for add-role/remove-role)')
    parser.add_argument("--no-copy-role-assignments", action="store_true",
                         help="For --action break: don't copy existing role assignments from the parent list")
    parser.add_argument("--no-clear-sub-scopes", action="store_true",
                         help="For --action break: don't clear unique permissions on child objects")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    return parser.parse_args()


def main_process(args, logger):
    if args.action in ("add-role", "remove-role") and (not args.principal or not args.role):
        logger.error("--principal and --role are required for --action %s", args.action)
        return

    if args.action in DESTRUCTIVE_ACTIONS and not args.yes:
        answer = input(
            f"Apply '{args.action}' permission change to item Id {args.item_id} "
            f"in '{args.list_title}' on {args.site_url}? [y/N] "
        )
        if answer.strip().lower() != "y":
            logger.info("Cancelled - no permission change was made")
            return

    ctx, _ = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)

    if args.action == "get":
        assignments = sharepoint.get_item_role_assignments(ctx, args.list_title, args.item_id)
        logger.info("Found %s role assignment(s):", len(assignments))
        for assignment in assignments:
            role_names = ", ".join(r.properties.get("Name") for r in assignment.role_definition_bindings)
            logger.info("- %s: %s", assignment.member.properties.get("Title"), role_names)

    elif args.action == "break":
        sharepoint.break_item_role_inheritance(
            ctx, args.list_title, args.item_id,
            copy_role_assignments=not args.no_copy_role_assignments,
            clear_sub_scopes=not args.no_clear_sub_scopes,
        )
        logger.info("Broke role inheritance on item Id: %s in '%s'", args.item_id, args.list_title)

    elif args.action == "reset":
        sharepoint.reset_item_role_inheritance(ctx, args.list_title, args.item_id)
        logger.info("Reset role inheritance on item Id: %s in '%s'", args.item_id, args.list_title)

    elif args.action == "add-role":
        sharepoint.add_item_role(ctx, args.list_title, args.item_id, args.principal, args.role)
        logger.info("Granted '%s' to '%s' on item Id: %s in '%s'", args.role, args.principal, args.item_id, args.list_title)

    elif args.action == "remove-role":
        sharepoint.remove_item_role(ctx, args.list_title, args.item_id, args.principal, args.role)
        logger.info("Revoked '%s' from '%s' on item Id: %s in '%s'", args.role, args.principal, args.item_id, args.list_title)


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "set_item_permission")

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
