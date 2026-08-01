# Connect to SharePoint Site

Connects to a SharePoint site interactively (browser sign-in) using
`Office365-REST-Python-Client` for SharePoint calls and `msal` for authentication,
then prints the site's Title and Url.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Configuration
Edit these constants in `connect_to_site.py` for your environment:
- `CLIENT_ID` — Azure AD app registration Client ID (currently set to the same app used for interactive auth in the PowerShell scripts)
- `TENANT_ID` — `"common"`, or your tenant domain (e.g. `"bsonedev.onmicrosoft.com"`)
- Default `--site-url` value

## Run it
```
python connect_to_site.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality
```
A browser window opens for you to sign in. On success it prints the site's Title and Url.

## How auth works
1. `msal.PublicClientApplication.acquire_token_interactive()` opens a browser and returns a token dict.
2. `office365`'s `ClientContext.with_access_token()` expects a `TokenResponse` object, not the raw dict —
   so the token is wrapped with `TokenResponse.from_json(result)` before being returned.

## Logging
Logs are written to `Logs/connect_to_site_<date>.log` (created automatically), with a per-run
CorrelationID and 7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end (interactive sign-in + site info printed)
