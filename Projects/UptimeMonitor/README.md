# Uptime Monitor

Checks one or more URLs and reports whether each is up (status < 400) or down
(status >= 400, or a network error), with response time. Can run a single pass
(default) or repeated rounds within one execution, logging state changes
(UP → DOWN / DOWN → UP) as they happen.

## Prerequisites
```
pip install requests
```

## Run it
```
# Single check (default)
python monitor_uptime.py --urls https://example.com https://api.github.com

# From a file (one URL per line)
python monitor_uptime.py --urls-file sites.txt

# 5 rounds, 30 seconds apart, within one run
python monitor_uptime.py --urls-file sites.txt --count 5 --interval 30
```

## Output
Per URL per round: `UP`/`DOWN`, status code (or the network error message if the
request failed entirely), and response time in ms. If a URL's state changes between
rounds within the same run, an extra `!! State change` line is logged.

## For continuous/unattended monitoring
A single run still has a finite lifetime (`--count` rounds, then it exits and logs
"Script finished"). For genuinely ongoing monitoring, schedule this script to run
periodically (e.g. Windows Task Scheduler) rather than passing a very large `--count`.

## Tested
Verified live against three real cases: a healthy site (`api.github.com` → UP, 200),
an intentional 404 (`httpbin.org/status/404` → DOWN), and a nonexistent domain → DOWN
with a DNS resolution error message. Also verified multi-round timing (`--count 2
--interval 2` took ~2.2s total, confirming no sleep after the last round) and
`--urls-file` input, including a mix of UP (200) and DOWN (500) results in one run.

## Logging
Logs are written to `Logs/monitor_uptime_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (UP/DOWN/network-error classification, multi-round
  timing, urls-file input) — state-change detection logic wasn't exercised live since
  I couldn't make a real site's status flip on demand, but the comparison logic is
  simple and directly testable if you want to add a unit test for it
