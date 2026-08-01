"""
Demo for file upload/download: upload_file, download_file. Self-contained -
creates a small temp local text file, uploads it, downloads it back to a
different local path, and verifies the content round-trips correctly. No CLI
args, no logging scaffolding.

Note: the uploaded file is NOT auto-removed from SharePoint afterward (there's
no delete_file function in this library yet) - clean it up manually if needed.

Requires:
    pip install Office365-REST-Python-Client msal

EXAMPLE
    python demo_file_transfer.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # for `import sharepoint`

import sharepoint

SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"
FOLDER_URL = "/sites/bsonequality/Shared Documents"  # <-- change to a real server-relative library/folder path

SCRIPT_FOLDER = Path(__file__).resolve().parent
UPLOAD_SOURCE = SCRIPT_FOLDER / "upload_demo.txt"
DOWNLOAD_TARGET = SCRIPT_FOLDER / "download_demo.txt"


def main():
    print("Connecting...")
    ctx, _ = sharepoint.connect(SITE_URL, CLIENT_ID, TENANT_ID)
    print("Connected.\n")

    content = "sharepoint lib file transfer demo\n"
    UPLOAD_SOURCE.write_text(content, encoding="utf-8")

    print(f"--- upload_file('{FOLDER_URL}', '{UPLOAD_SOURCE.name}') ---")
    uploaded_file = sharepoint.upload_file(ctx, FOLDER_URL, str(UPLOAD_SOURCE))
    server_relative_url = uploaded_file.properties.get("ServerRelativeUrl")
    print(f"Uploaded to: {server_relative_url}")

    print(f"\n--- download_file('{server_relative_url}') ---")
    sharepoint.download_file(ctx, server_relative_url, str(DOWNLOAD_TARGET))
    downloaded_content = DOWNLOAD_TARGET.read_text(encoding="utf-8")
    print(f"Downloaded to: {DOWNLOAD_TARGET}")
    print(f"Round-trip content match: {downloaded_content == content}")

    print("\nAll checks completed. Note: the uploaded file remains in SharePoint - remove it manually if needed.")


if __name__ == "__main__":
    main()
