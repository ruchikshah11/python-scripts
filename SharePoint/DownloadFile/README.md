# Download File

Downloads a file from a SharePoint document library to a local path. Equivalent to
PnP PowerShell's `Get-PnPFile`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python download_file.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --file-url "/sites/bsonequality/Shared Documents/report.docx" --output "C:/downloaded.docx"
```
`--file-url` is the server-relative file URL (starts with `/sites/...`). A browser window
opens for interactive sign-in (same app registration used across the other
[SharePoint](..) scripts).

## Output
Logs the local path the file was saved to.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `download_file()` — see that README for the
full function reference.

## Logging
Logs are written to `Logs/download_file_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
