# Get Connection

Connects to a SharePoint site interactively and prints details about the active
connection — site URL, connected user, tenant, client ID, token type/scope, and
token expiry. Equivalent in spirit to PowerShell's `Get-PnPConnection`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python get_connection.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality
```
A browser window opens for interactive sign-in (same app registration used across
the other [SharePoint](..) scripts).

## Output
`Site URL`, `Web Title`, `Connected As`, `Tenant Id`, `Client Id`, `Token Type`,
`Token Scope`, `Token Expires At`.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `connect()` and `get_connection_info()` —
see that README for the full function reference. This script itself is just the CLI
wrapper + logging (via [sp_logging](../common/README.md)) around those two calls.

## Logging
Logs are written to `Logs/get_connection_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
