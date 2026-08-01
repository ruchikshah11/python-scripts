# Get Field

Gets site or list fields (columns). Equivalent to PnP PowerShell's `Get-PnPField`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
# All site fields
python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality

# All fields on a specific list
python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents"

# One field by internal name or title (site-scoped)
python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --field-name "Title"

# One field on a specific list
python get_field.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --list-title "Documents" --field-name "Title"
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## Output
Without `--field-name`: Title + InternalName for every matching field.
With `--field-name`: Title, InternalName, FieldTypeKind, Required.

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `get_fields()` / `get_field()` — see that
README for the full function reference.

## Logging
Logs are written to `Logs/get_field_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
