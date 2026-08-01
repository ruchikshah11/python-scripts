# Add List Item

Adds a new item to a SharePoint list. Equivalent to PnP PowerShell's `Add-PnPListItem`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python add_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --fields "{\"Title\": \"New Item\"}"
```
`--fields` takes a JSON dict of internal field name -> value. A browser window opens for
interactive sign-in (same app registration used across the other [SharePoint](..) scripts).

## Output
Logs the new item's Id.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `add_list_item()` — see that README for the
full function reference.

## Logging
Logs are written to `Logs/add_list_item_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
