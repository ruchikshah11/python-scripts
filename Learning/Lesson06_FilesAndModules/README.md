# Lesson 6: Files, JSON/CSV, and Modules

## Topics
- `with open(path, mode) as f:` — auto-closes the file (vs `Get-Content`/`Set-Content`)
- Reading/writing plain text files
- `json.dump()` / `json.load()` (file <-> dict) vs `ConvertTo-Json` / `ConvertFrom-Json`
- `json.dumps()` (with an "s") — dict -> JSON string, no file involved
- `csv.DictWriter` / `csv.DictReader` vs `Export-Csv` / `Import-Csv`
- Modules: standard library needs no install; third-party needs `pip install X`
  (vs `Install-Module X` / `Import-Module X`)

## Run it
```
python lesson06.py
```
This creates `sample.txt`, `sample.json`, and `sample.csv` in this folder — check them out after running.

## Exercise
At the bottom of `lesson06.py`:
1. `config` dict with `site_url` and `retries`
2. Write to `config.json`, read it back into `loaded_config`, print it
3. Write `people.csv` with 3 rows (name, age), read it back and print each row

## Status
- [ ] Exercise completed
