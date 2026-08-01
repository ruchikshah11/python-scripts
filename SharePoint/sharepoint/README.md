# sharepoint

Personal SharePoint helper library (Ruchik Shah). Wraps `Office365-REST-Python-Client`
+ `msal` so scripts can call plain functions instead of repeating auth/REST boilerplate —
similar in spirit to PnP PowerShell's `Get-PnP*` cmdlets, translated to Python's
import-a-module style.

Not meant to be run directly — it's a library, imported by other scripts.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Functions
| Function | Returns | Like (PnP PowerShell) |
|---|---|---|
| `connect(site_url, client_id, tenant_id, logger=None)` | `(ctx, token_result)` — authenticated `ClientContext` via interactive sign-in, plus the raw MSAL token | `Connect-PnPOnline -Interactive` |
| `get_connection_info(ctx, token_result, client_id, site_url)` | dict — site url, web title, connected user, tenant id, client id, token type/scope/expiry | `Get-PnPConnection` |
| `get_lists(ctx)` | loaded list collection | `Get-PnPList` |
| `get_list(ctx, list_title)` | single loaded `List` object | `Get-PnPList -Identity <title>` |
| `get_list_items(ctx, list_title, top=10)` | loaded items (max `top`) | `Get-PnPListItem` |
| `add_list_item(ctx, list_title, fields)` | created `ListItem` | `Add-PnPListItem` |
| `update_list_item(ctx, list_title, item_id, fields, system_update=False)` | updated `ListItem`. `system_update=True` skips versioning/Modified fields/workflows | `Set-PnPListItem` / `Set-PnPListItem -SystemUpdate` |
| `delete_list_item(ctx, list_title, item_id, permanent=False)` | `None`. `permanent=True` purges from the Recycle Bin immediately | `Remove-PnPListItem` / `Remove-PnPListItem` + `Clear-PnPRecycleBinItem` |
| `upload_file(ctx, folder_server_relative_url, local_file_path)` | uploaded `File` object (files up to 4MB) | `Add-PnPFile` |
| `download_file(ctx, file_server_relative_url, local_file_path)` | `None` - saves to `local_file_path` | `Get-PnPFile` |
| `get_fields(ctx, list_title=None)` | loaded field collection - site-scoped or list-scoped | `Get-PnPField` |
| `get_field(ctx, field_name, list_title=None)` | single loaded `Field` | `Get-PnPField -Identity <name>` |
| `get_content_types(ctx, list_title=None)` | loaded content type collection - site-scoped or list-scoped | `Get-PnPContentType` |
| `get_content_type(ctx, name)` | single loaded `ContentType` | `Get-PnPContentType -Identity <name>` |
| `get_site_users(ctx)` | loaded user collection - every user with access, not just group members | `Get-PnPUser` |
| `get_groups(ctx)` | loaded group collection | `Get-PnPGroup` |
| `get_group(ctx, group_name)` | single loaded `Group` | `Get-PnPGroup -Identity <name>` |
| `get_associated_group(ctx, group_type)` | loaded `Group` - `group_type` is `"owner"`/`"member"`/`"visitor"` | `Get-PnPGroup -AssociatedOwnerGroup` / `-AssociatedMemberGroup` / `-AssociatedVisitorGroup` |
| `get_group_members(ctx, group_name)` | loaded user collection | `Get-PnPGroupMembers` |
| `break_item_role_inheritance(ctx, list_title, item_id, copy_role_assignments=True, clear_sub_scopes=True)` | `None` | `$item.BreakRoleInheritance(...)` |
| `reset_item_role_inheritance(ctx, list_title, item_id)` | `None` | `$item.ResetRoleInheritance()` |
| `get_item_role_assignments(ctx, list_title, item_id)` | loaded role assignment collection | `Get-PnPListItemPermission` |
| `add_item_role(ctx, list_title, item_id, principal_name, role_name)` | `None` | `Set-PnPListItemPermission -AddRole` |
| `remove_item_role(ctx, list_title, item_id, principal_name, role_name)` | `None` | `Set-PnPListItemPermission -RemoveRole` |
| `export_term_group(ctx, group_name, token_result)` | dict snapshot (name/termSets/terms/labels) - **NOT PnP-template XML**, see note below | `Export-PnPTermGroupToXml` (in spirit only) |
| `export_term_store(ctx, token_result)` | list of dict snapshots, one per term group - same shape as above | `Export-PnPTermGroupToXml` run against every group |
| `get_terms_for_set(ctx, term_set_id, token_result)` | flat list of `{"id", "label"}` dicts - every non-deprecated term in one term set | (no direct PnP equivalent - closest is filtering `Get-PnPTaxonomyItem`'s output) |

No config (client ID, tenant ID, site URL) lives in this module — every caller passes
its own values in, so the same library works across different app registrations/tenants
without editing shared code.

### A note on delete and the Recycle Bin
SharePoint has no single API call that deletes a list item while bypassing the Recycle
Bin entirely. `delete_list_item(..., permanent=True)` reflects that reality honestly: it
calls `recycle()` (moves the item to the Recycle Bin, same as `permanent=False`), then
immediately purges that specific Recycle Bin entry — mirroring what you'd get from
`Remove-PnPListItem` followed by `Clear-PnPRecycleBinItem` in PnP PowerShell.

### A note on `export_term_group`/`export_term_store` and PnP templates
`Export-PnPTermGroupToXml` (and `Get-PnPSiteTemplate` / `Invoke-PnPSiteTemplate` /
`Invoke-PnPTenantTemplate`) all depend on PnP's own provisioning-template XML schema and
its execution engine - a large .NET component nobody has reimplemented in Python.
`export_term_group()`/`export_term_store()` are deliberately different, honest things: a
plain JSON snapshot of term group structure (term sets, terms, labels) for
backup/reference/diffing. They are **not** re-importable by PnP PowerShell or anything
else - there is no Python path to real PnP-template compatibility.

Both functions take `token_result` (the raw MSAL token from `connect()`) and hit the
SharePoint v2.1 Term Store REST API directly via `requests`, rather than going through
`Office365-REST-Python-Client`'s taxonomy object model. That model's internal path names
(`termGroups`/`termSets`) turned out not to match the actual documented API
(`groups`/`sets`/`terms`), which silently returned empty results against a real tenant
instead of erroring - the raw REST approach here sidesteps that mismatch entirely.

## Usage
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # SharePoint/ folder

import sharepoint

ctx, token_result = sharepoint.connect(site_url, client_id, tenant_id)
lists = sharepoint.get_lists(ctx)
target_list = sharepoint.get_list(ctx, "Documents")
items = sharepoint.get_list_items(ctx, "Documents", top=25)
info = sharepoint.get_connection_info(ctx, token_result, client_id, site_url)

new_item = sharepoint.add_list_item(ctx, "Documents", {"Title": "New Item"})
sharepoint.update_list_item(ctx, "Documents", 1, {"Title": "Renamed"})
sharepoint.update_list_item(ctx, "Documents", 1, {"Title": "Renamed"}, system_update=True)
sharepoint.delete_list_item(ctx, "Documents", 1)                    # to Recycle Bin
sharepoint.delete_list_item(ctx, "Documents", 1, permanent=True)    # Recycle Bin + purge

uploaded = sharepoint.upload_file(ctx, "/sites/mysite/Shared Documents", "C:/report.docx")
sharepoint.download_file(ctx, "/sites/mysite/Shared Documents/report.docx", "C:/downloaded.docx")

fields = sharepoint.get_fields(ctx)                          # site fields
fields = sharepoint.get_fields(ctx, list_title="Documents")   # list fields
field = sharepoint.get_field(ctx, "Title")

content_types = sharepoint.get_content_types(ctx)                          # site content types
content_types = sharepoint.get_content_types(ctx, list_title="Documents")   # list's assignable content types
content_type = sharepoint.get_content_type(ctx, "Document")

users = sharepoint.get_site_users(ctx)
groups = sharepoint.get_groups(ctx)
group = sharepoint.get_group(ctx, "Members")
owners = sharepoint.get_associated_group(ctx, "owner")
members = sharepoint.get_group_members(ctx, "Members")

sharepoint.break_item_role_inheritance(ctx, "Documents", 1)
assignments = sharepoint.get_item_role_assignments(ctx, "Documents", 1)
sharepoint.add_item_role(ctx, "Documents", 1, "user@contoso.com", "Read")
sharepoint.remove_item_role(ctx, "Documents", 1, "user@contoso.com", "Read")
sharepoint.reset_item_role_inheritance(ctx, "Documents", 1)

snapshot = sharepoint.export_term_group(ctx, "MyTermGroup", token_result)   # NOT PnP-template-compatible
all_groups = sharepoint.export_term_store(ctx, token_result)               # every term group at once
terms = sharepoint.get_terms_for_set(ctx, term_set_id, token_result)       # flat [{"id", "label"}, ...]
```

See [Demo/demo_sharepoint.py](../Demo/demo_sharepoint.py) for a runnable example that
exercises the read-oriented functions.

## Used by
- [ConnectToSite](../ConnectToSite/README.md)
- [GetList](../GetList/README.md)
- [GetListItems](../GetListItems/README.md)
- [GetConnection](../GetConnection/README.md)
- [AddListItem](../AddListItem/README.md)
- [UpdateListItem](../UpdateListItem/README.md)
- [DeleteListItem](../DeleteListItem/README.md)
- [UploadFile](../UploadFile/README.md)
- [DownloadFile](../DownloadFile/README.md)
- [GetField](../GetField/README.md)
- [GetContentTypes](../GetContentTypes/README.md)
- [GetGroup](../GetGroup/README.md)
- [SetItemPermission](../SetItemPermission/README.md)
- [ExportTermGroup](../ExportTermGroup/README.md)
- [Demo](../Demo/README.md)
- [SPDummyDataGenerator](../../DesktopApps/SPDummyDataGenerator/README.md) (also uses `get_site_users` and `get_terms_for_set`)

## Status
- [ ] Verified working end-to-end (interactive sign-in + all 27 functions)
