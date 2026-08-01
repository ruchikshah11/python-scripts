"""
SYNOPSIS
    Generates cryptographically secure random passwords (using the `secrets`
    module, not `random`), or checks the strength of an existing password
    and gives specific feedback.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Adjust COMMON_PASSWORDS or the scoring weights in score_password() if
      you want a stricter/looser strength check

EXAMPLE
    python password_tool.py generate
    python password_tool.py generate --length 20 --count 3
    python password_tool.py generate --no-symbols
    python password_tool.py check --password "Tr0ub4dor&3"

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import getpass
import importlib
import logging
import re
import secrets
import string
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = []  # secrets, string, re are standard library

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
LOG_FILE_NAME = LOGS_DIRECTORY / f"password_tool_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

CORRELATION_ID = str(uuid.uuid4())[:11]
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?"

# A small sample of extremely common passwords - real deployments should use a much
# larger breached-password list (e.g. Have I Been Pwned's), this is just illustrative.
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "letmein", "admin", "welcome",
    "iloveyou", "monkey", "football", "abc123", "password1", "111111", "12345678",
}
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
    logger = logging.getLogger("password_tool")
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
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate a random password")
    generate_parser.add_argument("--length", type=int, default=16)
    generate_parser.add_argument("--count", type=int, default=1)
    generate_parser.add_argument("--no-uppercase", action="store_true")
    generate_parser.add_argument("--no-lowercase", action="store_true")
    generate_parser.add_argument("--no-digits", action="store_true")
    generate_parser.add_argument("--no-symbols", action="store_true")

    check_parser = subparsers.add_parser("check", help="Check the strength of a password")
    check_parser.add_argument("--password", default=None,
                               help="Password to check. If omitted, you'll be prompted "
                                    "securely (input hidden, not saved to shell history).")

    return parser.parse_args()


def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    """Generates a cryptographically secure password using `secrets`, guaranteeing
    at least one character from each enabled category."""
    categories = []
    if use_lower:
        categories.append(string.ascii_lowercase)
    if use_upper:
        categories.append(string.ascii_uppercase)
    if use_digits:
        categories.append(string.digits)
    if use_symbols:
        categories.append(SYMBOLS)

    if not categories:
        raise ValueError("At least one character category must be enabled")
    if length < len(categories):
        raise ValueError(f"--length must be at least {len(categories)} to include one of each enabled category")

    all_characters = "".join(categories)

    # Guarantee one character from each category, then fill the rest randomly
    password_chars = [secrets.choice(category) for category in categories]
    password_chars += [secrets.choice(all_characters) for _ in range(length - len(categories))]

    # Shuffle securely (Fisher-Yates using secrets.randbelow) so the guaranteed
    # category characters aren't always in the same leading positions
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def has_repeated_run(password, run_length=3):
    return re.search(r"(.)\1{" + str(run_length - 1) + ",}", password) is not None


def has_sequential_run(password, run_length=3):
    """Detects ascending or descending runs of consecutive character codes,
    e.g. "abc", "cba", "123", "321" (run_length or longer)."""
    for i in range(len(password) - run_length + 1):
        window = password[i:i + run_length]
        codes = [ord(c) for c in window]
        ascending = all(codes[k] + 1 == codes[k + 1] for k in range(len(codes) - 1))
        descending = all(codes[k] - 1 == codes[k + 1] for k in range(len(codes) - 1))
        if ascending or descending:
            return True
    return False


def score_password(password):
    """Returns (score 0-100, label, list of feedback strings)."""
    feedback = []
    score = 0

    length = len(password)
    if length < 8:
        feedback.append("Too short - use at least 8 characters (12+ recommended)")
    elif length < 12:
        score += 20
    elif length < 16:
        score += 35
    else:
        score += 50

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in SYMBOLS or not c.isalnum() for c in password)

    if has_lower:
        score += 10
    else:
        feedback.append("Add a lowercase letter")
    if has_upper:
        score += 10
    else:
        feedback.append("Add an uppercase letter")
    if has_digit:
        score += 10
    else:
        feedback.append("Add a digit")
    if has_symbol:
        score += 15
    else:
        feedback.append("Add a symbol")

    if password.lower() in COMMON_PASSWORDS:
        score = min(score, 10)
        feedback.append("This is one of the most commonly used passwords - avoid it entirely")

    if has_repeated_run(password):
        score -= 15
        feedback.append("Avoid repeating the same character 3+ times in a row")

    if has_sequential_run(password):
        score -= 15
        feedback.append("Avoid sequential characters like 'abc' or '123'")

    score = max(0, min(100, score))

    if score <= 20:
        label = "Very Weak"
    elif score <= 40:
        label = "Weak"
    elif score <= 60:
        label = "Fair"
    elif score <= 80:
        label = "Strong"
    else:
        label = "Very Strong"

    return score, label, feedback


def main_process(args, logger):
    if args.command == "generate":
        use_upper = not args.no_uppercase
        use_lower = not args.no_lowercase
        use_digits = not args.no_digits
        use_symbols = not args.no_symbols

        logger.info("Generating %s password(s), length %s", args.count, args.length)
        for _ in range(args.count):
            password = generate_password(args.length, use_upper, use_lower, use_digits, use_symbols)
            # Printed directly to console, NEVER through the logger - the logger
            # persists to a file on disk, and a generated password is a secret
            # that must never be written to a log file.
            print(password)

    elif args.command == "check":
        # Prefer a hidden prompt over --password so the value isn't left in shell
        # history. Only the score/feedback is logged - never the password itself,
        # since that's the secret being evaluated and must not be persisted to disk.
        password = args.password if args.password is not None else getpass.getpass("Password to check: ")
        score, label, feedback = score_password(password)
        logger.info("Score: %s/100 (%s)", score, label)
        if feedback:
            for line in feedback:
                logger.info("- %s", line)
        else:
            logger.info("No issues found")


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
