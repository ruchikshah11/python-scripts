"""
SYNOPSIS
    A Tkinter desktop client over the `sharepoint` library (SharePoint/sharepoint) -
    connect to a site, browse its lists, view items in a selected list, edit
    an item's Title, and upload a file to a document library. Reuses the
    same tested library functions as the standalone SharePoint CLI scripts -
    nothing about SharePoint access is reimplemented here.

DESCRIPTION
    Connecting is interactive (a browser window opens for sign-in), so it
    runs on a background thread to keep the GUI responsive while you sign in.

EXAMPLE
    python sharepoint_explorer.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-31
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import importlib
import logging
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

#region Module Dependency Check
REQUIRED_MODULES = ["msal", "office365"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)
#endregion

PYTHON_ROOT = Path(__file__).resolve().parent.parent.parent
SHAREPOINT_FOLDER = PYTHON_ROOT / "SharePoint"
sys.path.insert(0, str(SHAREPOINT_FOLDER))               # for `import sharepoint` (package)
sys.path.insert(0, str(SHAREPOINT_FOLDER / "common"))     # for `import sp_logging`

import sharepoint

# Same Azure AD app registration Client ID used across the SharePoint CLI scripts.
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"
DEFAULT_SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"


class TextWidgetLogHandler(logging.Handler):
    """Appends formatted log records into a Tkinter Text widget."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        message = self.format(record)

        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", message + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

        self.text_widget.after(0, append)


class SharePointExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SharePoint Explorer")
        self.root.geometry("900x650")

        self.ctx = None

        # --- Connection bar ---
        connection_frame = ttk.Frame(root)
        connection_frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(connection_frame, text="Site URL:").pack(side="left")
        self.site_url_entry = ttk.Entry(connection_frame, width=50)
        self.site_url_entry.insert(0, DEFAULT_SITE_URL)
        self.site_url_entry.pack(side="left", padx=8)

        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self._on_connect)
        self.connect_button.pack(side="left")

        self.connection_status = ttk.Label(connection_frame, text="Not connected")
        self.connection_status.pack(side="left", padx=8)

        # --- Main split: lists on the left, items on the right ---
        main_pane = ttk.PanedWindow(root, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=8, pady=8)

        lists_frame = ttk.LabelFrame(main_pane, text="Lists")
        main_pane.add(lists_frame, weight=1)

        self.lists_tree = ttk.Treeview(lists_frame, columns=("count",), show="tree headings", height=20)
        self.lists_tree.heading("#0", text="Title")
        self.lists_tree.heading("count", text="Items")
        self.lists_tree.column("count", width=60, anchor="center")
        self.lists_tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.lists_tree.bind("<<TreeviewSelect>>", self._on_select_list)

        items_frame = ttk.LabelFrame(main_pane, text="Items")
        main_pane.add(items_frame, weight=2)

        self.items_tree = ttk.Treeview(items_frame, columns=("id", "title", "modified"), show="headings", height=15)
        self.items_tree.heading("id", text="Id")
        self.items_tree.heading("title", text="Title")
        self.items_tree.heading("modified", text="Modified")
        self.items_tree.column("id", width=50, anchor="center")
        self.items_tree.column("title", width=250)
        self.items_tree.column("modified", width=150)
        self.items_tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.items_tree.bind("<<TreeviewSelect>>", self._on_select_item)

        # --- Edit panel ---
        edit_frame = ttk.LabelFrame(items_frame, text="Edit selected item's Title")
        edit_frame.pack(fill="x", padx=4, pady=4)
        self.edit_title_entry = ttk.Entry(edit_frame, width=40)
        self.edit_title_entry.pack(side="left", padx=4, pady=4)
        ttk.Button(edit_frame, text="Save Title", command=self._on_save_title).pack(side="left", padx=4)

        # --- Upload panel ---
        upload_frame = ttk.LabelFrame(root, text="Upload a file")
        upload_frame.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(upload_frame, text="Folder URL:").pack(side="left", padx=4)
        self.upload_folder_entry = ttk.Entry(upload_frame, width=40)
        self.upload_folder_entry.insert(0, "/sites/bsonequality/Shared Documents")
        self.upload_folder_entry.pack(side="left", padx=4)
        ttk.Button(upload_frame, text="Choose File & Upload", command=self._on_upload_file).pack(side="left", padx=4)

        # --- Status/log panel ---
        self.status_text = tk.Text(root, height=6, state="disabled", wrap="word")
        self.status_text.pack(fill="x", padx=8, pady=(0, 8))

        self.logger = logging.getLogger("sharepoint_explorer")
        self.logger.setLevel(logging.INFO)
        handler = TextWidgetLogHandler(self.status_text)
        handler.setFormatter(logging.Formatter("%(asctime)s  %(message)s", datefmt="%H:%M:%S"))
        self.logger.addHandler(handler)

        self._list_titles_by_row = {}     # Treeview item id -> list title
        self._item_ids_by_row = {}        # Treeview item id -> SharePoint item Id
        self._current_list_title = None

    # ---------- helpers ----------

    def run_in_background(self, target):
        threading.Thread(target=target, daemon=True).start()

    def show_error(self, title, exception):
        self.logger.info("Error: %s", exception)
        messagebox.showerror(title, str(exception))

    # ---------- Connect ----------

    def _on_connect(self):
        site_url = self.site_url_entry.get().strip()
        if not site_url:
            messagebox.showwarning("Connect", "Enter a site URL first")
            return

        self.connect_button.configure(state="disabled")
        self.connection_status.configure(text="Connecting (check for a browser sign-in window)...")

        def task():
            try:
                ctx, _token_result = sharepoint.connect(site_url, CLIENT_ID, TENANT_ID, self.logger)
                self.ctx = ctx
                self.root.after(0, lambda: self.connection_status.configure(text=f"Connected: {site_url}"))
                self._load_lists()
            except Exception as ex:
                self.root.after(0, lambda: self.connection_status.configure(text="Not connected"))
                self.show_error("Connect", ex)
            finally:
                self.root.after(0, lambda: self.connect_button.configure(state="normal"))

        self.run_in_background(task)

    # ---------- Lists ----------

    def _load_lists(self):
        try:
            lists = sharepoint.get_lists(self.ctx)
            rows = [(sp_list.properties["Title"], sp_list.properties["ItemCount"]) for sp_list in lists]
        except Exception as ex:
            self.show_error("Lists", ex)
            return

        def update():
            self.lists_tree.delete(*self.lists_tree.get_children())
            self._list_titles_by_row = {}
            for title, count in rows:
                row_id = self.lists_tree.insert("", "end", text=title, values=(count,))
                self._list_titles_by_row[row_id] = title

        self.root.after(0, update)

    def _on_select_list(self, _event):
        selection = self.lists_tree.selection()
        if not selection:
            return
        list_title = self._list_titles_by_row.get(selection[0])
        if not list_title:
            return
        self._current_list_title = list_title
        self._load_items(list_title)

    # ---------- Items ----------

    def _load_items(self, list_title):
        def task():
            try:
                items = sharepoint.get_list_items(self.ctx, list_title, top=50)
                rows = [
                    (item.properties.get("ID"), item.properties.get("Title"), item.properties.get("Modified"))
                    for item in items
                ]
            except Exception as ex:
                self.show_error("Items", ex)
                return

            def update():
                self.items_tree.delete(*self.items_tree.get_children())
                self._item_ids_by_row = {}
                for item_id, title, modified in rows:
                    row_id = self.items_tree.insert("", "end", values=(item_id, title, modified))
                    self._item_ids_by_row[row_id] = item_id
                self.logger.info("Loaded %s item(s) from '%s'", len(rows), list_title)

            self.root.after(0, update)

        self.run_in_background(task)

    def _on_select_item(self, _event):
        selection = self.items_tree.selection()
        if not selection:
            return
        values = self.items_tree.item(selection[0], "values")
        title = values[1] if len(values) > 1 else ""
        self.edit_title_entry.delete(0, "end")
        self.edit_title_entry.insert(0, title or "")

    def _on_save_title(self):
        selection = self.items_tree.selection()
        if not selection or not self._current_list_title:
            messagebox.showinfo("Edit", "Select an item first")
            return

        item_id = self._item_ids_by_row.get(selection[0])
        new_title = self.edit_title_entry.get()

        def task():
            try:
                sharepoint.update_list_item(self.ctx, self._current_list_title, item_id, {"Title": new_title})
                self.logger.info("Updated item #%s Title -> '%s'", item_id, new_title)
                self._load_items(self._current_list_title)
            except Exception as ex:
                self.show_error("Edit", ex)

        self.run_in_background(task)

    # ---------- Upload ----------

    def _on_upload_file(self):
        if self.ctx is None:
            messagebox.showinfo("Upload", "Connect to a site first")
            return

        local_path = filedialog.askopenfilename()
        if not local_path:
            return

        folder_url = self.upload_folder_entry.get().strip()

        def task():
            try:
                uploaded_file = sharepoint.upload_file(self.ctx, folder_url, local_path)
                self.logger.info("Uploaded to: %s", uploaded_file.properties.get("ServerRelativeUrl"))
            except Exception as ex:
                self.show_error("Upload", ex)

        self.run_in_background(task)


def main():
    root = tk.Tk()
    SharePointExplorerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
