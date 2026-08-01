"""
SYNOPSIS
    A Tkinter desktop tool that connects to a SharePoint list and populates
    it with realistic random ("dummy") data - covering every field type the
    REST API can write (Text, Note, Choice, MultiChoice, Number, Currency,
    Boolean, DateTime, URL, Guid, Geolocation, Person/Group, Lookup, and
    Managed Metadata, single- and multi-value). A Python + Tkinter port of
    the existing C# CSOM tool at C:\\Ruchik\\Csom\\SPDummyDataGenerator,
    reusing this workspace's `sharepoint` library for auth/connection instead
    of replicating that tool's separate cookie-based "web login" popup.

DESCRIPTION
    Connect to a site (interactive sign-in, same as every other SharePoint
    script here), pick a list, review the field schema grid (Internal Name /
    Title / Type / Required / Populated?), set an item count and batch size,
    then click Generate. Items are created in batches - `batch_size` items'
    worth of add_item() calls are queued, then flushed with one
    execute_query(), same batching model as the original tool. Unlike the
    C# version (which has to CastTo<T>() + Include() each field type
    separately via CSOM), this reads a field's full set of type-specific
    properties (Choices, LookupList, TermSetId, etc.) in one REST round-trip.

    Reference data needed for realistic values (site users, lookup-list
    candidate items, Managed Metadata terms) is fetched once per Generate
    click and cached for that run - see value_generator.py.

EXAMPLE
    python spdummydatagenerator.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-01
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import importlib
import logging
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

#region Module Dependency Check
REQUIRED_MODULES = ["msal", "office365", "faker"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        install_name = "Faker" if module_name == "faker" else module_name
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {install_name}")
        sys.exit(1)
#endregion

SCRIPT_FOLDER = Path(__file__).resolve().parent
PYTHON_ROOT = SCRIPT_FOLDER.parent.parent
SHAREPOINT_FOLDER = PYTHON_ROOT / "SharePoint"
sys.path.insert(0, str(SCRIPT_FOLDER))                    # for schema_reader / value_generator / item_creator
sys.path.insert(0, str(SHAREPOINT_FOLDER))                # for `import sharepoint`

import sharepoint
import schema_reader
from item_creator import create_items
from value_generator import DummyValueGenerator

# Same Azure AD app registration Client ID used across the SharePoint CLI scripts.
CLIENT_ID = "7441600d-eba1-4ac3-8d11-08d662dc84b0"
TENANT_ID = "common"
DEFAULT_SITE_URL = "https://bsonedev.sharepoint.com/sites/bsonequality"

DEFAULT_ITEM_COUNT = 25
DEFAULT_BATCH_SIZE = 20


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


class SPDummyDataGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SP Dummy Data Generator")
        self.root.geometry("900x700")

        self.ctx = None
        self.token_result = None
        self._writable_fields = []       # schema_reader output for the selected list
        self._list_titles = []           # combobox index -> list title

        self._build_connection_bar()
        self._build_list_selector()
        self._build_fields_grid()
        self._build_generate_bar()
        self._build_log_panel()

    # ---------- layout ----------

    def _build_connection_bar(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=8, pady=8)

        ttk.Label(frame, text="Site URL:").pack(side="left")
        self.site_url_entry = ttk.Entry(frame, width=50)
        self.site_url_entry.insert(0, DEFAULT_SITE_URL)
        self.site_url_entry.pack(side="left", padx=8)

        self.connect_button = ttk.Button(frame, text="Connect", command=self._on_connect)
        self.connect_button.pack(side="left")

        self.connection_status = ttk.Label(frame, text="Not connected")
        self.connection_status.pack(side="left", padx=8)

    def _build_list_selector(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(frame, text="List:").pack(side="left")
        self.list_combo = ttk.Combobox(frame, state="disabled", width=40)
        self.list_combo.pack(side="left", padx=8)
        self.list_combo.bind("<<ComboboxSelected>>", lambda event: self._on_select_list())

    def _build_fields_grid(self):
        frame = ttk.LabelFrame(self.root, text="Fields that will be populated")
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("internal_name", "title", "type", "required", "supported")
        self.fields_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for column, heading, width in (
            ("internal_name", "Internal Name", 180),
            ("title", "Title", 180),
            ("type", "Type", 140),
            ("required", "Required", 70),
            ("supported", "Populated?", 80),
        ):
            self.fields_tree.heading(column, text=heading)
            self.fields_tree.column(column, width=width, anchor="w" if column in ("internal_name", "title") else "center")
        self.fields_tree.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_generate_bar(self):
        frame = ttk.LabelFrame(self.root, text="Generate")
        frame.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(frame, text="Item count:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.item_count_spin = ttk.Spinbox(frame, from_=1, to=100000, width=8)
        self.item_count_spin.set(DEFAULT_ITEM_COUNT)
        self.item_count_spin.grid(row=0, column=1, padx=(0, 16))

        ttk.Label(frame, text="Batch size:").grid(row=0, column=2, padx=8, sticky="w")
        self.batch_size_spin = ttk.Spinbox(frame, from_=1, to=5000, width=8)
        self.batch_size_spin.set(DEFAULT_BATCH_SIZE)
        self.batch_size_spin.grid(row=0, column=3, padx=(0, 16))

        self.generate_button = ttk.Button(frame, text="Generate dummy items", command=self._on_generate,
                                           state="disabled")
        self.generate_button.grid(row=0, column=4, padx=8)

        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=5, sticky="ew", padx=8, pady=(0, 8))
        frame.columnconfigure(4, weight=1)

        self.progress_label = ttk.Label(frame, text="")
        self.progress_label.grid(row=2, column=0, columnspan=5, sticky="w", padx=8, pady=(0, 8))

    def _build_log_panel(self):
        self.log_text = tk.Text(self.root, height=8, state="disabled", wrap="word")
        self.log_text.pack(fill="x", padx=8, pady=(0, 8))

        self.logger = logging.getLogger("spdummydatagenerator")
        self.logger.setLevel(logging.INFO)
        handler = TextWidgetLogHandler(self.log_text)
        handler.setFormatter(logging.Formatter("%(asctime)s  %(message)s", datefmt="%H:%M:%S"))
        self.logger.addHandler(handler)

    # ---------- helpers ----------

    def run_in_background(self, target):
        threading.Thread(target=target, daemon=True).start()

    def show_error(self, title, exception):
        self.logger.error("%s error: %s", title, exception)
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
                ctx, token_result = sharepoint.connect(site_url, CLIENT_ID, TENANT_ID, self.logger)
                self.ctx = ctx
                self.token_result = token_result
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
            titles = sorted(
                sp_list.properties["Title"] for sp_list in lists if not sp_list.properties.get("Hidden")
            )
        except Exception as ex:
            self.show_error("Lists", ex)
            return

        def update():
            self._list_titles = titles
            self.list_combo.configure(values=titles, state="readonly")
            self.logger.info("Loaded %s list(s)", len(titles))

        self.root.after(0, update)

    def _on_select_list(self):
        list_title = self.list_combo.get()
        if not list_title:
            return

        self.generate_button.configure(state="disabled")
        self.fields_tree.delete(*self.fields_tree.get_children())

        def task():
            try:
                fields = schema_reader.get_writable_fields(self.ctx, list_title)
            except Exception as ex:
                self.show_error("Fields", ex)
                return

            def update():
                self._writable_fields = fields
                for field in fields:
                    self.fields_tree.insert("", "end", values=(
                        field["internal_name"], field["title"], field["type_as_string"],
                        "Yes" if field["required"] else "No",
                        "Yes" if field["is_supported"] else "No",
                    ))
                supported_count = sum(f["is_supported"] for f in fields)
                self.logger.info(
                    "Loaded %s writable field(s) on '%s' (%s will be populated)",
                    len(fields), list_title, supported_count,
                )
                self.generate_button.configure(state="normal")

            self.root.after(0, update)

        self.run_in_background(task)

    # ---------- Generate ----------

    def _on_generate(self):
        list_title = self.list_combo.get()
        if not list_title:
            messagebox.showinfo("Generate", "Select a list first")
            return

        try:
            item_count = int(self.item_count_spin.get())
            batch_size = int(self.batch_size_spin.get())
        except ValueError:
            messagebox.showwarning("Generate", "Item count and batch size must be numbers")
            return

        supported_fields = [f for f in self._writable_fields if f["is_supported"]]
        if not supported_fields:
            messagebox.showwarning("Generate", "No populatable fields found on this list")
            return

        self.generate_button.configure(state="disabled")
        self.progress.configure(maximum=item_count, value=0)
        self.progress_label.configure(text="")
        start_time = time.perf_counter()

        def progress_callback(created_so_far):
            def update():
                self.progress.configure(value=created_so_far)
                elapsed = time.perf_counter() - start_time
                self.progress_label.configure(text=f"{created_so_far}/{item_count} items, {elapsed:.1f}s elapsed")

            self.root.after(0, update)

        def task():
            try:
                content_type_ids = schema_reader.get_assignable_content_type_ids(self.ctx, list_title)
                generator = DummyValueGenerator(self.ctx, self.token_result, self.logger)

                self.logger.info("Generating %s item(s) on '%s' (batch size %s)", item_count, list_title, batch_size)
                created = create_items(
                    self.ctx, list_title, supported_fields, content_type_ids,
                    item_count, batch_size, generator, progress_callback, self.logger,
                )
                self.logger.info("Done - created %s item(s)", created)
            except Exception as ex:
                self.show_error("Generate", ex)
            finally:
                self.root.after(0, lambda: self.generate_button.configure(state="normal"))

        self.run_in_background(task)


def main():
    root = tk.Tk()
    SPDummyDataGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
