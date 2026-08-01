# Get Group

Gets SharePoint groups, an associated Owner/Member/Visitor group, or a group's members.
Equivalent to PnP PowerShell's `Get-PnPGroup` / `Get-PnPGroupMembers`.

## Prerequisites
```
pip install Office365-REST-Python-Client msal
```

## Run it
```
# All groups on the site
python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality

# One group by name
python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "Members"

# The site's associated Owner/Member/Visitor group
python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --associated member

# A group's members instead of the group's own details
python get_group.py --site-url https://bsonedev.sharepoint.com/sites/bsonequality --group-name "Members" --members
```
A browser window opens for interactive sign-in (same app registration used across the
other [SharePoint](..) scripts).

## Output
- No args: Title of every group on the site
- `--group-name` / `--associated`: Title, Id, OwnerTitle of that group
- `+ --members`: Title + Email of every member in the resolved group

## How it works
Uses [sharepoint](../sharepoint/README.md)'s `get_groups()`, `get_group()`,
`get_associated_group()`, and `get_group_members()` — see that README for the full
function reference.

## Logging
Logs are written to `Logs/get_group_<date>.log`, with a per-run CorrelationID and
7-day retention.

## Status
- [ ] Verified working end-to-end
