# Set Item Permission

Manages a list item's permissions: break/reset inheritance, view current role
assignments, or add/remove a role for a principal. Equivalent to PnP PowerShell's
`Get-PnPListItemPermission` / `Set-PnPListItemPermission`.

**Destructive** for `break`/`reset`/`add-role`/`remove-role`. Prompts for confirmation
unless `--yes` is passed.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
# View current permissions
python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action get

# Break inheritance (item gets its own unique permissions)
python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action break

# Reset back to inheriting from the list
python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action reset

# Grant a role (item must already have unique permissions - run --action break first)
python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action add-role --principal "user@contoso.com" --role "Read"

# Revoke a role
python set_item_permission.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --item-id 1 --action remove-role --principal "user@contoso.com" --role "Read"
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## Flags
- `--no-copy-role-assignments` — for `break`: don't copy the list's existing permissions onto the item first
- `--no-clear-sub-scopes` — for `break`: don't clear unique permissions already set on child objects
- `--yes` — skip the confirmation prompt

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `break_item_role_inheritance()`,
`reset_item_role_inheritance()`, `get_item_role_assignments()`, `add_item_role()`, and
`remove_item_role()` — see that README for the full function reference.

## Logging
Logs are written to `Logs/set_item_permission_<date>.log`, with a per-run CorrelationID
and 7-day retention.

## Status
- [ ] Verified working end-to-end
