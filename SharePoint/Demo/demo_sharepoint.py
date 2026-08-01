"""
Demo script for the sharepoint library - exercises the read-only functions
directly (connect, get_connection_info, get_lists, get_list, get_list_items,
get_fields, get_content_types, get_groups, get_associated_group,
get_group_members) with plain print() output. No CLI args, no logging
scaffolding - this is meant to be a quick smoke test / usage example, not a
production script.

Not covered here (need extra args this demo can't guess, or are
destructive/mutating): add_list_item, update_list_item, delete_list_item,
upload_file, download_file, break_item_role_inheritance,
reset_item_role_inheritance, add_item_role, remove_item_role,
export_term_group. Try those individually via their own CLI scripts
(e.g. AddListItem, SetItemPermission, ExportTermGroup).

Requires:
    pip install Office365-REST-Python-Client msal

EXAMPLE
    python demo_sharepoint.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # for `import sharepoint`

import sharepoint

SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"


def main():
    print("Connecting...")
    ctx, token_result = sharepoint.connect(SITE_URL, CLIENT_ID, TENANT_ID)
    print("Connected.\n")

    print("--- get_connection_info ---")
    info = sharepoint.get_connection_info(ctx, token_result, CLIENT_ID, SITE_URL)
    for key, value in info.items():
        print(f"{key}: {value}")

    print("\n--- get_lists ---")
    lists = sharepoint.get_lists(ctx)
    for sp_list in lists:
        print(f"- {sp_list.properties['Title']} (ItemCount: {sp_list.properties['ItemCount']})")

    if len(lists) > 0:
        first_list_title = lists[0].properties["Title"]

        print(f"\n--- get_list('{first_list_title}') ---")
        target_list = sharepoint.get_list(ctx, first_list_title)
        print(f"Title: {target_list.properties['Title']}")
        print(f"Id: {target_list.properties['Id']}")
        print(f"ItemCount: {target_list.properties['ItemCount']}")

        print(f"\n--- get_list_items('{first_list_title}', top=5) ---")
        items = sharepoint.get_list_items(ctx, first_list_title, top=5)
        for item in items:
            print(f"Id: {item.properties.get('ID')} | Title: {item.properties.get('Title')}")
    else:
        print("No lists found on this site - skipping get_list/get_list_items checks")

    print("\n--- get_fields (site fields, first 10) ---")
    fields = sharepoint.get_fields(ctx)
    for field in list(fields)[:10]:
        print(f"- {field.properties.get('Title')} (InternalName: {field.properties.get('InternalName')})")

    if len(fields) > 0:
        first_field_name = fields[0].properties.get("InternalName")
        print(f"\n--- get_field('{first_field_name}') ---")
        field = sharepoint.get_field(ctx, first_field_name)
        print(f"Title: {field.properties.get('Title')}")
        print(f"FieldTypeKind: {field.properties.get('FieldTypeKind')}")

    print("\n--- get_content_types (first 10) ---")
    content_types = sharepoint.get_content_types(ctx)
    for content_type in list(content_types)[:10]:
        print(f"- {content_type.properties.get('Name')} (Group: {content_type.properties.get('Group')})")

    if len(content_types) > 0:
        first_content_type_name = content_types[0].properties.get("Name")
        print(f"\n--- get_content_type('{first_content_type_name}') ---")
        content_type = sharepoint.get_content_type(ctx, first_content_type_name)
        print(f"Name: {content_type.properties.get('Name')}")
        print(f"Id: {content_type.properties.get('StringId')}")

    print("\n--- get_groups ---")
    groups = sharepoint.get_groups(ctx)
    for group in groups:
        print(f"- {group.properties.get('Title')}")

    if len(groups) > 0:
        first_group_title = groups[0].properties.get("Title")
        print(f"\n--- get_group('{first_group_title}') ---")
        group = sharepoint.get_group(ctx, first_group_title)
        print(f"Title: {group.properties.get('Title')}")
        print(f"Id: {group.properties.get('Id')}")

    print("\n--- get_associated_group('member') ---")
    member_group = sharepoint.get_associated_group(ctx, "member")
    member_group_title = member_group.properties.get("Title")
    print(f"Title: {member_group_title}")

    print(f"\n--- get_group_members('{member_group_title}') ---")
    members = sharepoint.get_group_members(ctx, member_group_title)
    for member in members:
        print(f"- {member.properties.get('Title')} ({member.properties.get('Email')})")

    print("\nAll checks completed.")


if __name__ == "__main__":
    main()
