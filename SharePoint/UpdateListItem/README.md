# Update List Item

Updates an existing SharePoint list item by ID. Equivalent to PnP PowerShell's
`Set-PnPListItem` (and `Set-PnPListItem -SystemUpdate` via `--system-update`).

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python update_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --fields "{\"Title\": \"Renamed\"}"

# System update - no new version, Modified/Modified By untouched, no workflows triggered
python update_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --fields "{\"Title\": \"Renamed\"}" --system-update
```
`--fields` takes a JSON dict of internal field name -> value. A browser window opens for
interactive sign-in (same app registration used across the other [SharePoint](..) scripts).

## `--system-update` explained
By default, updating an item creates a new version and updates `Modified`/`Modified By`,
same as `Set-PnPListItem`. Pass `--system-update` when you want to change field values
without any of that side effect - no new version, `Modified`/`Modified By` untouched, no
workflows triggered. Same distinction PnP PowerShell makes with `Set-PnPListItem -SystemUpdate`.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `update_list_item()` — see that README for
the full function reference.

## Logging
Logs are written to `Logs/update_list_item_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
