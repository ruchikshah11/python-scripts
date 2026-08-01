# Export Term Group

Exports a taxonomy term group (term sets + terms) to a JSON file for backup/reference.

**Not equivalent to `Export-PnPTermGroupToXml`.** That cmdlet produces XML in PnP's own
provisioning-template schema, which no Python library reimplements (see
[sharepoint/README.md](../sharepoint/README.md) for why). This script produces a plain
JSON snapshot instead — useful for backup, diffing, or documentation, but **not**
re-importable via PnP PowerShell or any other tool.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
python export_term_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "MyTermGroup" --output "C:/MyTermGroup.json"
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## Output
A JSON file shaped like:
```json
{
  "name": "MyTermGroup",
  "termSets": [
    {
      "id": "...",
      "name": "MyTermSet",
      "terms": [
        {"id": "...", "labels": [{"name": "Term1", "languageTag": "en-US", "isDefault": true}]}
      ]
    }
  ]
}
```

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `export_term_group()`, which goes through
the newer Term Store REST API (v2.1) via `TaxonomyService` — see that README's note on
`export_term_group` and PnP templates for the full explanation of scope/limitations.

## Logging
Logs are written to `Logs/export_term_group_<date>.log`, with a per-run CorrelationID
and 7-day retention.

## Status
- [ ] Verified working end-to-end
