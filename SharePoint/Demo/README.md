# Demo: sharepoint

Smoke-test / usage examples for the [sharepoint](../sharepoint/README.md) library —
5 scripts together exercise all 25 functions directly with plain `print()` output.
No CLI args, no logging scaffolding; meant to be read top-to-bottom as a quick
reference for how to call `sharepoint` directly, not production scripts.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

---

## demo_sharepoint.py — read-only checks

### Configuration
`SITE_URL`, `CLIENT_ID`, `TENANT_ID` at the top.

### Run it
```
python demo_sharepoint.py
```

### What it checks
`connect`, `get_connection_info`, `get_lists`, `get_list`, `get_list_items`,
`get_fields`, `get_field`, `get_content_types`, `get_content_type`, `get_groups`,
`get_group`, `get_associated_group`, `get_group_members` — 13 functions. Picks the
first list/field/content type/group found rather than requiring hardcoded names, so
it runs on any site. If the site has no lists, the `get_list`/`get_list_items` checks
are skipped with a message rather than failing.

### Status
- [ ] Verified working end-to-end

---

## demo_export_term_group.py — taxonomy export

### Configuration
`SITE_URL`, `CLIENT_ID`, `TENANT_ID` at the top — no group name needed.

### Run it
```
python demo_export_term_group.py
```
Writes `term_store_export_demo.json` (every term group) and
`term_group_export_demo.json` (one group, picked from whatever was found) to this
folder.

### What it checks
`export_term_store` (exports every term group in the term store - runs on any
tenant, no guessing) and `export_term_group` (for one group name, taken dynamically
from the `export_term_store` result).

**Reminder:** NOT PnP-template-compatible — see
[sharepoint/README.md](../sharepoint/README.md)'s note on `export_term_group` for why.

### Status
- [ ] Verified working end-to-end

---

## demo_list_item_crud.py — list item write operations

**Mutates data**, but is self-contained: creates its own throwaway item, updates it
twice, then deletes it (to the Recycle Bin, not permanently) — safe to re-run.

### Configuration
`LIST_TITLE` must be a real list with a `Title` field (most lists have one).

### Run it
```
python demo_list_item_crud.py
```

### What it checks
`add_list_item`, `update_list_item` (normal), `update_list_item` (`system_update=True`),
`delete_list_item`.

### Status
- [ ] Verified working end-to-end

---

## demo_file_transfer.py — file upload/download

### Configuration
`FOLDER_URL` must be a real server-relative document library/folder path.

### Run it
```
python demo_file_transfer.py
```
Creates a small local text file, uploads it, downloads it back to a different local
path, and checks the content round-trips correctly.

### What it checks
`upload_file`, `download_file`.

**Note:** the uploaded file is NOT auto-removed from SharePoint afterward (no
`delete_file` function exists yet) — clean it up manually if needed.

### Status
- [ ] Verified working end-to-end

---

## demo_item_permissions.py — item permission operations

**Destructive-ish**, but resets the item back to inherited permissions at the end —
safe to re-run.

### Configuration
`LIST_TITLE` and `ITEM_ID` must point to a real, existing item. `PRINCIPAL_NAME` must
be a real user login or group name on your tenant.

### Run it
```
python demo_item_permissions.py
```

### What it checks
`break_item_role_inheritance`, `get_item_role_assignments`, `add_item_role`,
`remove_item_role`, `reset_item_role_inheritance` — full cycle, ending back where it
started.

### Status
- [ ] Verified working end-to-end

---

## Not covered by any demo
`delete_list_item(..., permanent=True)` — the permanent-delete path isn't exercised
here since it's genuinely destructive with no undo; test it deliberately via
[DeleteListItem](../DeleteListItem/README.md)'s `--permanent` flag instead, on a
throwaway item.
