"""
SYNOPSIS
    Pulls public GitHub stats for a user (aggregate across all public repos:
    total stars/forks, language breakdown, top repos) or for one specific
    repo (stars, forks, open issues, language, description). No API key
    required - uses GitHub's public REST API, subject to its unauthenticated
    rate limit (60 requests/hour per IP).

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update default args (e.g. --user) for typical usage

EXAMPLE
    python github_stats.py --user torvalds
    python github_stats.py --user torvalds --repo linux

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import argparse
import importlib
import logging
import sys
import time
import uuid
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = ["requests"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)

import requests
#endregion

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"github_stats_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

API_BASE = "https://api.github.com"
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
    logger = logging.getLogger("github_stats")
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
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--repo", default=None, help="Repo name (owned by --user) for single-repo stats instead of aggregate")
    return parser.parse_args()


def get_user_profile(username, logger):
    logger.info("Fetching profile for '%s'", username)
    response = requests.get(f"{API_BASE}/users/{username}")
    if response.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found")
    response.raise_for_status()
    return response.json()


def get_all_repos(username, logger):
    """Returns every public repo for username, paginating 100 at a time."""
    repos = []
    page = 1
    while True:
        logger.info("Fetching repos page %s for '%s'", page, username)
        response = requests.get(
            f"{API_BASE}/users/{username}/repos",
            params={"per_page": 100, "page": page, "type": "owner"},
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_repo(username, repo_name, logger):
    logger.info("Fetching repo '%s/%s'", username, repo_name)
    response = requests.get(f"{API_BASE}/repos/{username}/{repo_name}")
    if response.status_code == 404:
        raise ValueError(f"Repo '{username}/{repo_name}' not found")
    response.raise_for_status()
    return response.json()


def main_process(args, logger):
    profile = get_user_profile(args.user, logger)
    logger.info("--- Profile: %s ---", args.user)
    logger.info("Name: %s", profile.get("name") or "(not set)")
    logger.info("Public repos: %s", profile.get("public_repos"))
    logger.info("Followers: %s | Following: %s", profile.get("followers"), profile.get("following"))

    if args.repo:
        repo = get_repo(args.user, args.repo, logger)
        logger.info("--- Repo: %s/%s ---", args.user, args.repo)
        logger.info("Description: %s", repo.get("description") or "(none)")
        logger.info("Language: %s", repo.get("language") or "(not detected)")
        logger.info("Stars: %s | Forks: %s | Open issues: %s",
                     repo.get("stargazers_count"), repo.get("forks_count"), repo.get("open_issues_count"))
        logger.info("Last updated: %s", repo.get("updated_at"))
        return

    repos = get_all_repos(args.user, logger)
    total_stars = sum(r["stargazers_count"] for r in repos)
    total_forks = sum(r["forks_count"] for r in repos)
    language_counts = Counter(r["language"] for r in repos if r["language"])
    top_repo = max(repos, key=lambda r: r["stargazers_count"], default=None)

    logger.info("--- Aggregate across %s repo(s) ---", len(repos))
    logger.info("Total stars: %s | Total forks: %s", total_stars, total_forks)
    logger.info("Languages: %s", dict(language_counts.most_common()))
    if top_repo:
        logger.info("Most starred: %s (%s stars)", top_repo["name"], top_repo["stargazers_count"])


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
