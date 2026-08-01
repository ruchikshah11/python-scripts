"""
SYNOPSIS
    Sends an email notification via SMTP. Credentials are read from
    environment variables - never hardcoded, never passed as CLI arguments
    (which would leak into shell history).

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Set the required environment variables before running (see below)

    Required environment variables:
        SMTP_HOST      - e.g. smtp.gmail.com or smtp.office365.com
        SMTP_PORT      - e.g. 587 (STARTTLS)
        SMTP_USERNAME  - the account you're sending FROM
        SMTP_PASSWORD  - an APP PASSWORD, not your normal account password
                         (Gmail/Microsoft 365 both require a separate app
                         password when 2FA is enabled - use one, don't use
                         your real login password here)

    PowerShell example (current session only):
        $env:SMTP_HOST = "smtp.gmail.com"
        $env:SMTP_PORT = "587"
        $env:SMTP_USERNAME = "you@gmail.com"
        $env:SMTP_PASSWORD = "your-16-char-app-password"

EXAMPLE
    python send_notification.py --to someone@example.com --subject "Job done" --body "The nightly sync finished."
    python send_notification.py --to someone@example.com --subject "Report" --body-file report.txt

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import logging
import os
import smtplib
import sys
import time
import uuid
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # smtplib, email are standard library

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"send_notification_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

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
    logger = logging.getLogger("send_notification")
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
    parser.add_argument("--to", required=True, action="append", help="Recipient email address. Repeat --to for multiple recipients.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", default=None, help="Email body text")
    parser.add_argument("--body-file", default=None, help="Read the email body from this file instead of --body")
    return parser.parse_args()


def get_smtp_settings(logger):
    """Reads SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD from the
    environment. Raises ValueError with a clear message if any are missing -
    never falls back to a hardcoded default for credentials."""
    required_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
    missing = [name for name in required_vars if not os.environ.get(name)]
    if missing:
        raise ValueError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "See the script's docstring for how to set them."
        )

    logger.info("Using SMTP host %s:%s as %s", os.environ["SMTP_HOST"], os.environ["SMTP_PORT"], os.environ["SMTP_USERNAME"])
    return {
        "host": os.environ["SMTP_HOST"],
        "port": int(os.environ["SMTP_PORT"]),
        "username": os.environ["SMTP_USERNAME"],
        "password": os.environ["SMTP_PASSWORD"],
    }


def send_email(smtp_settings, to_addresses, subject, body):
    message = EmailMessage()
    message["From"] = smtp_settings["username"]
    message["To"] = ", ".join(to_addresses)
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(smtp_settings["host"], smtp_settings["port"], timeout=30) as server:
        server.starttls()
        server.login(smtp_settings["username"], smtp_settings["password"])
        server.send_message(message)


def main_process(args, logger):
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()
    elif args.body is not None:
        body = args.body
    else:
        raise ValueError("Either --body or --body-file is required")

    smtp_settings = get_smtp_settings(logger)

    logger.info("Sending to %s | Subject: %s", ", ".join(args.to), args.subject)
    send_email(smtp_settings, args.to, args.subject, body)
    logger.info("Sent successfully")


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
