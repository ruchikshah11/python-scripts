"""
sharepoint - personal SharePoint helper library (Ruchik Shah).

Wraps Office365-REST-Python-Client + msal so scripts can call plain functions
instead of repeating auth/REST boilerplate - similar in spirit to PnP
PowerShell's Get-PnP* cmdlets, translated to Python's import-a-module style.

Usage:
    import sharepoint

    ctx, token_result = sharepoint.connect(site_url, client_id, tenant_id, logger)
    lists = sharepoint.get_lists(ctx)
    target_list = sharepoint.get_list(ctx, "Documents")
    items = sharepoint.get_list_items(ctx, "Documents", top=25)
    info = sharepoint.get_connection_info(ctx, token_result, client_id, site_url)

    new_item = sharepoint.add_list_item(ctx, "Documents", {"Title": "New Item"})
    updated_item = sharepoint.update_list_item(ctx, "Documents", 1, {"Title": "Renamed"})
    # system_update=True: no new version, Modified/Modified By untouched, no workflows - like Set-PnPListItem -SystemUpdate
    sharepoint.update_list_item(ctx, "Documents", 1, {"Title": "Renamed"}, system_update=True)

    sharepoint.delete_list_item(ctx, "Documents", 1)                     # to Recycle Bin (recoverable)
    sharepoint.delete_list_item(ctx, "Documents", 1, permanent=True)     # Recycle Bin + purge (NOT recoverable)

    uploaded = sharepoint.upload_file(ctx, "/sites/mysite/Shared Documents", "C:/report.docx")
    sharepoint.download_file(ctx, "/sites/mysite/Shared Documents/report.docx", "C:/downloaded.docx")

    fields = sharepoint.get_fields(ctx)                       # site fields
    fields = sharepoint.get_fields(ctx, list_title="Documents")  # list fields
    field = sharepoint.get_field(ctx, "Title")

    content_types = sharepoint.get_content_types(ctx)                        # site content types
    content_types = sharepoint.get_content_types(ctx, list_title="Documents")  # list's assignable content types
    content_type = sharepoint.get_content_type(ctx, "Document")

    users = sharepoint.get_site_users(ctx)   # every user with access, not just group members
    groups = sharepoint.get_groups(ctx)
    group = sharepoint.get_group(ctx, "Members")
    owners = sharepoint.get_associated_group(ctx, "owner")   # "owner" | "member" | "visitor"
    members = sharepoint.get_group_members(ctx, "Members")

    sharepoint.break_item_role_inheritance(ctx, "Documents", 1)
    assignments = sharepoint.get_item_role_assignments(ctx, "Documents", 1)
    sharepoint.add_item_role(ctx, "Documents", 1, "user@contoso.com", "Read")
    sharepoint.remove_item_role(ctx, "Documents", 1, "user@contoso.com", "Read")
    sharepoint.reset_item_role_inheritance(ctx, "Documents", 1)

    # NOT PnP-template-compatible - see sharepoint/taxonomy.py docstring
    # (both take token_result - they use the raw access token for direct REST calls)
    snapshot = sharepoint.export_term_group(ctx, "MyTermGroup", token_result)
    all_groups = sharepoint.export_term_store(ctx, token_result)  # every term group in the term store
    terms = sharepoint.get_terms_for_set(ctx, term_set_id, token_result)  # flat [{"id", "label"}, ...]

Requires:
    pip install Office365-REST-Python-Client msal
"""

import importlib
import sys

REQUIRED_MODULES = ["msal", "office365"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)

from .connection import connect, get_connection_info
from .lists import get_lists, get_list, get_list_items, add_list_item, update_list_item, delete_list_item
from .files import upload_file, download_file
from .fields import get_fields, get_field
from .content_types import get_content_types, get_content_type
from .permissions import (
    get_site_users,
    get_groups,
    get_group,
    get_associated_group,
    get_group_members,
    break_item_role_inheritance,
    reset_item_role_inheritance,
    get_item_role_assignments,
    add_item_role,
    remove_item_role,
)
from .taxonomy import export_term_group, export_term_store, get_terms_for_set

__all__ = [
    "connect",
    "get_connection_info",
    "get_lists",
    "get_list",
    "get_list_items",
    "add_list_item",
    "update_list_item",
    "delete_list_item",
    "upload_file",
    "download_file",
    "get_fields",
    "get_field",
    "get_content_types",
    "get_content_type",
    "get_site_users",
    "get_groups",
    "get_group",
    "get_associated_group",
    "get_group_members",
    "break_item_role_inheritance",
    "reset_item_role_inheritance",
    "get_item_role_assignments",
    "add_item_role",
    "remove_item_role",
    "export_term_group",
    "export_term_store",
    "get_terms_for_set",
]
