"""
SYNOPSIS
    Lesson 6: Files, JSON/CSV, and Modules - text file read/write, json.dump/
    load/dumps, csv.DictWriter/DictReader, and standard-library vs pip-
    installed modules.

DESCRIPTION
    Run this file top-to-bottom to see each concept's output (it creates
    sample.txt/json/csv in this folder), then complete the exercise at the
    bottom.

EXAMPLE
    python lesson06.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-29
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.2.0
"""

import json
import csv
from pathlib import Path

print("=" * 60)
print("LESSON 6: Files, JSON/CSV, and Modules")
print("=" * 60)

SCRIPT_FOLDER = Path(__file__).resolve().parent

print("\n--- Writing a text file ---")
# "with" auto-closes the file when the block ends
text_file = SCRIPT_FOLDER / "sample.txt"
with open(text_file, "w", encoding="utf-8") as f:
    f.write("Hello from Python\n")
    f.write("Second line\n")

print("\n--- Reading a text file ---")
with open(text_file, "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())   # .strip() removes the trailing newline

print("\n--- JSON ---")
data = {"name": "Ruchik", "age": 27, "skills": ["Python", "SharePoint", "Automation"]}

json_file = SCRIPT_FOLDER / "sample.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)   # dump() writes JSON directly to a file

with open(json_file, "r", encoding="utf-8") as f:
    loaded = json.load(f)          # load() reads JSON directly from a file
print(loaded["name"], loaded["skills"])

# json.dumps() (with an 's') converts to a STRING instead of writing to a file
json_string = json.dumps(data)
print(json_string)

print("\n--- CSV ---")
csv_file = SCRIPT_FOLDER / "sample.csv"
rows = [
    {"name": "Ruchik", "age": 27},
    {"name": "Kalpesh", "age": 30},
]
with open(csv_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerows(rows)

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])

print("\n--- Modules ---")
# Standard library modules (json, csv, pathlib, etc.) need no install - just import them.
# Third-party modules need: pip install <name>   (run in the terminal, not in the script)


# ============================================================
# EXERCISE - write your code below this line, then run:
#     python lesson06.py
# ============================================================
#
# 1. Create a dict `config` = {"site_url": "https://example.sharepoint.com", "retries": 3}
# 2. Write it to a file `config.json` in this folder using json.dump
# 3. Read it back with json.load into a variable `loaded_config` and print it
# 4. Write a CSV `people.csv` with 3 rows of your choosing (name, age columns),
#    then read it back and print each row

# --- write your code below this line ---
