# Upload File

Uploads a local file (up to 4MB) into a SharePoint document library folder. Equivalent
to PnP PowerShell's `Add-PnPFile`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python upload_file.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --folder-url "/sites/bsonequality/Shared Documents" --file "C:/report.docx"
```
`--folder-url` is the server-relative folder URL (starts with `/sites/...`). A browser
window opens for interactive sign-in (same app registration used across the other
[SharePoint](..) scripts).

## Output
Logs the uploaded file's server-relative URL.

## Limitation
This uses the simple upload path, which only supports files up to 4MB. Larger files need
a chunked/resumable upload, which isn't implemented here.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `upload_file()` — see that README for the
full function reference.

## Logging
Logs are written to `Logs/upload_file_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
