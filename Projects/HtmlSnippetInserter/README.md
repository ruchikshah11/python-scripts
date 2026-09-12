# HtmlSnippetInserter

Generic, config-driven text editor: inserts a snippet of text on its own line, immediately
before the first line containing a given marker string, in each of a list of files.
Python port of the PowerShell version at
`C:/Ruchik/powershell-scripts/SharePoint/Provisioning/Templates/Add-HtmlSnippetBeforeMarker/` -
keep both in sync if the config shape or matching/insertion rules change.

Not specific to email templates or HTML - works on any text file.

## How it works

Every edit is one `{file_path, marker, snippet}` object in the config's `edits` array:
- **Idempotent** - if `snippet` already appears anywhere in the file, it's skipped.
- **Indentation matches the marker's own line** - no hard-coded indent width.
- **Line-ending style is detected from the file itself** (CRLF vs LF) and preserved.
- A `marker` that doesn't match any line is reported and skipped.

## Run it
```
python insert_html_snippet_before_marker.py --dry-run
python insert_html_snippet_before_marker.py
python insert_html_snippet_before_marker.py --config-path "C:/some/other-config.json"
```
```json
{
  "dry_run": false,
  "edits": [
    {
      "file_path": "C:\\path\\to\\SomeTemplateEN.html",
      "marker": "<p>Thank You</p>",
      "snippet": "<p><b>[ApproverComments]</b></p>"
    }
  ]
}
```

## Encoding note (ported from a real bug in the PowerShell version)
The PowerShell script had a real bug: it named the line-ending separator `$newline` and the
to-be-inserted line `$newLine` - PowerShell variable names are case-insensitive, so those are
the *same* variable, and the second assignment silently clobbered the first. The file got
joined back together using the snippet text as the separator instead of a real newline.

Python doesn't have that specific hazard, but it has an analogous one: `Path.read_text()` /
`Path.write_text()` do **universal-newline translation** by default - silently turning every
`\r\n` into `\n` on read (and back on write), which would just as silently destroy a file's
real CRLF/LF convention. This script opens files explicitly with `newline=""` on both read and
write to disable that translation, so the file's actual line endings are read and written
byte-for-byte untouched.

## Tested
Verified against a real email-template file (`[ApproverComments]` line removed to simulate
the "missing" case): the real insertion path was exercised end-to-end, producing pure-CRLF
output (50 CRLF, 0 stray bare LF) and a second run correctly reporting the snippet already
present (idempotency). Also verified in dry-run mode against the 4 real files this was built
for (`bsoneQM{Document,Process}ApprovalNotifyApproved{EN,DE}.html`) - correctly reported all 4
already present, 0 changes.
