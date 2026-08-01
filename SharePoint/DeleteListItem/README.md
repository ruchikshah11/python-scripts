# Delete List Item

Deletes a SharePoint list item by ID — to the Recycle Bin by default, or permanently
with `--permanent`. Equivalent to PnP PowerShell's `Remove-PnPListItem` (and
`Remove-PnPListItem` + `Clear-PnPRecycleBinItem` combined, for `--permanent`).

**Destructive.** Prompts for confirmation unless `--yes` is passed.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python delete_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1

# Skip the confirmation prompt
python delete_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --yes

# Permanent delete - NOT recoverable afterward
python delete_list_item.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --permanent
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## `--permanent` explained
SharePoint has no single API call that deletes an item while bypassing the Recycle Bin
entirely. Without `--permanent`, the item is moved to the Recycle Bin and can be restored
later. With `--permanent`, this script moves it to the Recycle Bin and then immediately
purges that specific entry — same net effect as `Remove-PnPListItem` followed by
`Clear-PnPRecycleBinItem`, and NOT recoverable afterward.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `delete_list_item()` — see that README for
the full function reference.

## Logging
Logs are written to `Logs/delete_list_item_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
