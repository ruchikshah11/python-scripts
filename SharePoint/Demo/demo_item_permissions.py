"""
Demo for list item permission operations: break_item_role_inheritance,
get_item_role_assignments, add_item_role, remove_item_role,
reset_item_role_inheritance. Runs a full cycle and resets the item back to
inherited permissions at the end, so it's safe to re-run. No CLI args, no
logging scaffolding.

Requires:
    pip install Office365-REST-Python-Client msal

EXAMPLE
    python demo_item_permissions.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # for `import sharepoint`

import sharepoint

SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"
LIST_TITLE = "Documents"             # <-- change to a real list/library title
ITEM_ID = 1                          # <-- change to a real item Id in that list
PRINCIPAL_NAME = "user@contoso.com"  # <-- change to a real user login or group name
ROLE_NAME = "Read"


def print_assignments(ctx):
    assignments = sharepoint.get_item_role_assignments(ctx, LIST_TITLE, ITEM_ID)
    print(f"Found {len(assignments)} role assignment(s):")
    for assignment in assignments:
        role_names = ", ".join(role.properties.get("Name") for role in assignment.role_definition_bindings)
        print(f"- {assignment.member.properties.get('Title')}: {role_names}")


def main():
    print("Connecting...")
    ctx, _ = sharepoint.connect(SITE_URL, CLIENT_ID, TENANT_ID)
    print("Connected.\n")

    print(f"--- break_item_role_inheritance(item_id={ITEM_ID}) ---")
    sharepoint.break_item_role_inheritance(ctx, LIST_TITLE, ITEM_ID)
    print("Broke inheritance - item now has unique permissions")

    print("\n--- get_item_role_assignments (before) ---")
    print_assignments(ctx)

    print(f"\n--- add_item_role('{PRINCIPAL_NAME}', '{ROLE_NAME}') ---")
    sharepoint.add_item_role(ctx, LIST_TITLE, ITEM_ID, PRINCIPAL_NAME, ROLE_NAME)
    print("Role granted")

    print("\n--- get_item_role_assignments (after add) ---")
    print_assignments(ctx)

    print(f"\n--- remove_item_role('{PRINCIPAL_NAME}', '{ROLE_NAME}') ---")
    sharepoint.remove_item_role(ctx, LIST_TITLE, ITEM_ID, PRINCIPAL_NAME, ROLE_NAME)
    print("Role revoked")

    print(f"\n--- reset_item_role_inheritance(item_id={ITEM_ID}) ---")
    sharepoint.reset_item_role_inheritance(ctx, LIST_TITLE, ITEM_ID)
    print("Reset back to inherited permissions - item left in its original state")

    print("\nAll checks completed.")


if __name__ == "__main__":
    main()
