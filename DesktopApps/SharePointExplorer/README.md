# SharePoint Explorer

A Tkinter desktop client over the [`sharepoint`](../../SharePoint/sharepoint/README.md)
library — connect to a site, browse its lists, view items in a selected list, edit an
item's Title, and upload a file to a document library. Reuses the same tested library
functions as the standalone SharePoint CLI scripts (`GetList`, `GetListItems`,
`UpdateListItem`, `UploadFile`) — nothing about SharePoint access is reimplemented here.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python sharepoint_explorer.py
```
1. Enter a site URL (defaults to the same dev site the CLI scripts use) and click
   **Connect** — a browser window opens for interactive sign-in, same as every other
   SharePoint script in this workspace.
2. Click a list on the left to load its items on the right (top 50).
3. Click an item to load its Title into the edit box; change it and click **Save
   Title** to update it (via `update_list_item`, normal update — not `system_update`).
4. Use **Choose File & Upload** to pick a local file and upload it to the folder URL
   shown (files up to 4MB, same limitation as `UploadFile`).

Connecting and all list/item operations run on background threads so the window stays
responsive.

## Scope
This is a **read/browse + minimal edit** client, not a full SharePoint UI replacement:
- Lists: view only (Title, ItemCount)
- Items: view (Id, Title, Modified) + edit **Title only** — no other fields, no
  add/delete item support in the UI yet
- Files: upload only, no browsing/download in this version

## ⚠️ Testing limitation — please read
Connecting requires **your real Microsoft 365 credentials** via an interactive
browser sign-in — I have no way to complete that flow myself, and doing so would
require your login. What I verified:
- The script compiles and imports cleanly (all `sharepoint` library functions resolve
  correctly)
- No syntax/import errors on startup

**Not verified: the actual Connect → browse → edit → upload flow against a real
tenant.** Please run it yourself, sign in, and click through each panel to confirm it
behaves as expected — this is the same limitation noted for every interactive
SharePoint script built in this workspace.

## Logging
No separate log file — status messages (connection progress, load counts, errors)
appear in the in-app text panel only.

## Status
- [x] Compiles and imports cleanly
- [ ] **Full interactive flow (connect/browse/edit/upload) — untested, please verify
  yourself against a real site**
