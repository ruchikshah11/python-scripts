# Get List

Connects to a SharePoint site and retrieves list metadata — either every list
on the site, or a single list's details when `--list-title` is given.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
# List every list on the site
python get_list.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality

# Get details for one list
python get_list.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents"
```
A browser window opens for interactive sign-in (same app registration used in
[ConnectToSite](../ConnectToSite/README.md)).

## Output
- Without `--list-title`: Title + ItemCount for every list on the site
- With `--list-title`: Title, Id, ItemCount, BaseTemplate, LastItemModifiedDate

## Logging
Logs are written to `Logs/get_list_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
