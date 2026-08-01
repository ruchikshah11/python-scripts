# Get List Items

Connects to a SharePoint site and retrieves items from a specific list.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python get_list_items.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents"

# Limit / raise the number of items returned (default: 10)
python get_list_items.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Tasks" --top 25
```
A browser window opens for interactive sign-in (same app registration used in
[ConnectToSite](../ConnectToSite/README.md)).

## Output
Prints `Id | Title | Modified` for each item retrieved (up to `--top`).
Adjust the fields logged in `main_process()` in `get_list_items.py` if you need
different columns from the list.

## Logging
Logs are written to `Logs/get_list_items_<date>.log`, with a per-run CorrelationID
and 7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [ ] Verified working end-to-end
