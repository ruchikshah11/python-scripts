"""
Demo script for sharepoint.export_term_store() and export_term_group() -
direct usage example with plain print() output. No CLI args, no logging
scaffolding.

export_term_store() needs no group name - it exports every term group in the
term store, so this demo runs on any tenant without guessing names. It then
also demos export_term_group() for one specific group, picked dynamically
from whatever export_term_store() found (no hardcoded GROUP_NAME to get wrong).

Reminder: neither function is PnP-template-compatible (no
Export-PnPTermGroupToXml equivalent exists in Python) - see
sharepoint/README.md for why. These produce plain JSON snapshots for
backup/reference only.

Requires:
    pip install Office365-REST-Python-Client msal

EXAMPLE
    python demo_export_term_group.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # for `import sharepoint`

import sharepoint

SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"

SCRIPT_FOLDER = Path(__file__).resolve().parent
STORE_OUTPUT_FILE = SCRIPT_FOLDER / "term_store_export_demo.json"
GROUP_OUTPUT_FILE = SCRIPT_FOLDER / "term_group_export_demo.json"


def print_snapshot(snapshot):
    print(f"Name: {snapshot['name']}")
    print(f"Term sets: {len(snapshot['termSets'])}")
    for term_set in snapshot["termSets"]:
        print(f"- {term_set['name']} ({len(term_set['terms'])} term(s))")
        for term in term_set["terms"]:
            default_label = next(
                (label["name"] for label in term["labels"] if label["isDefault"]),
                term["labels"][0]["name"] if term["labels"] else "(no label)",
            )
            print(f"    - {default_label}")


def main():
    print("Connecting...")
    ctx, token_result = sharepoint.connect(SITE_URL, CLIENT_ID, TENANT_ID)
    print("Connected.\n")

    print("--- export_term_store (every term group) ---")
    all_groups = sharepoint.export_term_store(ctx, token_result)
    print(f"Found {len(all_groups)} term group(s):")
    for group_snapshot in all_groups:
        print(f"- {group_snapshot['name']} ({len(group_snapshot['termSets'])} term set(s))")

    with open(STORE_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_groups, f, indent=2)
    print(f"Full snapshot written to {STORE_OUTPUT_FILE}")

    if len(all_groups) == 0:
        print("\nNo term groups found on this tenant - skipping export_term_group check")
        print("\nAll checks completed.")
        return

    first_group_name = all_groups[0]["name"]
    print(f"\n--- export_term_group('{first_group_name}') ---")
    snapshot = sharepoint.export_term_group(ctx, first_group_name, token_result)
    print_snapshot(snapshot)

    with open(GROUP_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Full snapshot written to {GROUP_OUTPUT_FILE}")

    print("\nAll checks completed.")


if __name__ == "__main__":
    main()
