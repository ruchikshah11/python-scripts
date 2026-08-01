# GitHub Stats CLI

Pulls public GitHub stats for a user (aggregate across all public repos) or for one
specific repo — no API key required, uses GitHub's public REST API.

## Prerequisites
```
pip install requests
```

## Run it
```
# Aggregate stats across every public repo
python github_stats.py --user torvalds

# Stats for one specific repo
python github_stats.py --user torvalds --repo linux
```

## Output
- **Profile**: name, public repo count, followers/following
- **Aggregate mode**: total repos analyzed, total stars, total forks, language
  breakdown (repo count per language), most-starred repo
- **Single-repo mode** (`--repo`): description, language, stars, forks, open issues,
  last updated

## Notes
- Paginates through all of a user's repos (100 per page) for the aggregate view.
- Subject to GitHub's unauthenticated rate limit (60 requests/hour per IP) — fine for
  occasional use, but repeated runs in quick succession can hit it.
- Unknown username/repo → clear "not found" error, exit code 1.

## Logging
Logs are written to `Logs/github_stats_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (tested live: octocat aggregate, torvalds/linux
  single-repo, and an invalid-username error case)
