"""
Demo for list item write operations: add_list_item, update_list_item (normal
+ system_update), delete_list_item. Self-contained and safe to re-run - it
creates its own throwaway item, updates it twice, then deletes it (to the
Recycle Bin, not permanently) at the end. No CLI args, no logging scaffolding.

Requires:
    pip install Office365-REST-Python-Client msal

EXAMPLE
    python demo_list_item_crud.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # for `import sharepoint`

import sharepoint

SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"
LIST_TITLE = "Documents"  # <-- change to a real list title with a Title field (most lists have one)


def main():
    print("Connecting...")
    ctx, _ = sharepoint.connect(SITE_URL, CLIENT_ID, TENANT_ID)
    print("Connected.\n")

    print(f"--- add_list_item('{LIST_TITLE}') ---")
    new_item = sharepoint.add_list_item(ctx, LIST_TITLE, {"Title": "sharepoint lib demo item"})
    item_id = new_item.properties["Id"]
    print(f"Created Id: {item_id}")

    print(f"\n--- update_list_item(item_id={item_id}) ---")
    sharepoint.update_list_item(ctx, LIST_TITLE, item_id, {"Title": "sharepoint lib demo item (updated)"})
    print("Updated (normal - creates a new version, sets Modified)")

    print(f"\n--- update_list_item(item_id={item_id}, system_update=True) ---")
    sharepoint.update_list_item(
        ctx, LIST_TITLE, item_id, {"Title": "sharepoint lib demo item (system updated)"}, system_update=True
    )
    print("Updated (system_update - no new version, Modified untouched)")

    print(f"\n--- delete_list_item(item_id={item_id}) ---")
    sharepoint.delete_list_item(ctx, LIST_TITLE, item_id)
    print("Deleted (moved to Recycle Bin - not permanent, recoverable)")

    print("\nAll checks completed.")


if __name__ == "__main__":
    main()
