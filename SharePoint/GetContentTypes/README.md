# Get Content Types

Gets site content types. Equivalent to PnP PowerShell's `Get-PnPContentType`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
# All content types
python get_content_types.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality

# One content type by name
python get_content_types.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --content-type-name "Document"
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## Output
Without `--content-type-name`: Name + Group for every content type.
With `--content-type-name`: Name, Id, Group, Description.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `get_content_types()` / `get_content_type()`
— see that README for the full function reference.

## Logging
Logs are written to `Logs/get_content_types_<date>.log`, with a per-run CorrelationID
and 7-day retention.

## Status
- [ ] Verified working end-to-end
