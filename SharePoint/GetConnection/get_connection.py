"""
SYNOPSIS
    Connects to a SharePoint site interactively and prints details about the
    active connection - site URL, connected user, tenant, client ID, token
    type, and token expiry. Equivalent in spirit to PowerShell's Get-PnPConnection.
    Uses the sharepoint library (SharePoint/sharepoint) for the connection, and the
    shared sp_logging helper (SharePoint/common) for logging.

DESCRIPTION
    Copy this file as the starting point for a new SharePoint script, then:
    - Update default args (e.g. --site-url) for the target environment
    - Fill in main_process() with the script's actual logic

EXAMPLE
    python get_connection.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality

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
    return parser.parse_args()


def main_process(args, logger):
    ctx, token_result = sharepoint.connect(args.site_url, CLIENT_ID, TENANT_ID, logger)
    info = sharepoint.get_connection_info(ctx, token_result, CLIENT_ID, args.site_url)

    logger.info("Site URL: %s", info["site_url"])
    logger.info("Web Title: %s", info["web_title"])
    logger.info("Connected As: %s", info["connected_as"])
    logger.info("Tenant Id: %s", info["tenant_id"])
    logger.info("Client Id: %s", info["client_id"])
    logger.info("Token Type: %s", info["token_type"])
    logger.info("Token Scope: %s", info["token_scope"])
    logger.info("Token Expires At: %s", info["token_expires_at"])


def main():
    args = parse_args()
    logger, correlation_id = sp_logging.build_logger(SCRIPT_FOLDER, "get_connection")

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
