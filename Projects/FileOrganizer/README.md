# File Organizer

Organizes files in a folder into subfolders, either **by type** (Images, Documents,
Videos, Audio, Archives, Scripts, Other) or **by last-modified date** (`YYYY-MM`
subfolders). **Defaults to a dry run** that only prints what would happen — nothing
is moved until you pass `--apply`.

Only processes files directly inside the given folder, not subfolders — so it never
recurses into folders it already created on a previous run.

## Prerequisites
None beyond the standard library.

## Run it
```
# Preview only (default) - nothing is moved
python organize_files.py --path "C:/Users/me/Downloads"

# Actually move the files
python organize_files.py --path "C:/Users/me/Downloads" --apply

# Group by last-modified month instead of file type
python organize_files.py --path "C:/Users/me/Downloads" --by date --apply
```

## Categories (--by type)
| Category | Extensions |
|---|---|
| Images | .jpg .jpeg .png .gif .bmp .svg .webp .ico .tiff |
| Documents | .pdf .doc .docx .xls .xlsx .ppt .pptx .txt .csv .md .odt |
| Videos | .mp4 .mov .avi .mkv .wmv .flv .webm |
| Audio | .mp3 .wav .flac .aac .ogg .m4a |
| Archives | .zip .rar .7z .tar .gz .bz2 |
| Scripts | .py .ps1 .sh .js .bat |
| Other | anything else |

## Safety
- **Dry run by default** — you must pass `--apply` to move anything
- **Name collisions handled** — if the destination already has a same-named file, the
  moved file is renamed `name (1).ext`, `name (2).ext`, etc. rather than overwriting
- Invalid `--path` → clear error, exit code 1

## Tested
Verified against a temporary scratch folder with mixed file types (jpg, pdf, mp4, py,
an unknown extension): dry run left files untouched and printed the correct plan;
`--apply` moved every file into the right subfolder; a re-run with a duplicate
filename correctly created `photo1 (1).jpg` instead of overwriting; an invalid path
produced a clean error.

## Logging
Logs are written to `Logs/organize_files_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (dry run, apply, collision handling, invalid path —
  all tested against a scratch folder, not your real files)
