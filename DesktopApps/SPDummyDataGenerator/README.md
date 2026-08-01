# SP Dummy Data Generator

A Tkinter desktop tool that connects to an existing SharePoint list and fills
it with realistic random ("dummy") test data - a Python + Tkinter port of the
existing C# CSOM tool at `C:\Ruchik\Csom\SPDummyDataGenerator`. Like the
original, this only *populates* an existing list's existing fields - it never
creates lists, fields, or content types.

Reuses this workspace's [`sharepoint`](../../SharePoint/sharepoint/README.md)
library for connecting and reading list/field/content-type/user metadata,
rather than reimplementing SharePoint access. Two functions were added to
that shared library specifically to support this tool -
`get_site_users()` and `get_terms_for_set()` - since generating realistic
Person and Managed Metadata values needs real site users and real terms to
pick from.

## Prerequisites
```
pip install Office365-REST-Python-Client msal Faker
```

## Run it
```
python spdummydatagenerator.py
```
1. Enter a site URL (defaults to the same dev site the other SharePoint
   scripts use) and click **Connect** - a browser window opens for
   interactive sign-in, same as every other SharePoint script in this
   workspace.
2. Pick a list from the dropdown - the grid below fills in with every
   writable field on that list (Internal Name / Title / Type / Required /
   Populated?). "Populated? = No" means the field was recognized but skipped
   (see Scope below) - it's shown, not hidden, so you can see exactly what
   won't be touched.
3. Set an item count (1-100,000) and batch size (1-5,000 - how many items
   accumulate before one network round-trip), then click **Generate dummy
   items**. Progress bar and elapsed time update after each batch flush.

Every generated item shows your own signed-in account as Created By/Modified
By, since that's who's actually making the API calls - SharePoint always
stamps Author/Editor with whoever is signed in, and there's no supported way
to override that from a normal user account. (An attempt at an "Attribute to
System Account" option was tried and removed - even with `system_update()`,
it needs Full Control/site admin permissions to actually stick, which isn't
guaranteed, and it silently no-op'd in testing.)

## Field types supported
Text, Note (plain or rich), Choice, MultiChoice, Number, Currency, Boolean,
DateTime (date-only or date+time), URL, Guid, Geolocation, Person/Group
(single or multi-value, picked from real site users), Lookup (single or
multi-value, picked from up to 100 real items in the actual target list),
and Managed Metadata (single or multi-value, picked from real terms in the
field's actual bound term set, deprecated terms excluded).

## Scope (matches the original C# tool)
- **Never creates lists, fields, or content types** - only populates an
  existing list's existing schema.
- Hidden fields, read-only fields, and an explicit skip-list of system
  internal names (`ContentTypeId`, `Attachments`, `FileRef`, `_ModerationStatus`,
  etc. - see `schema_reader.SKIP_INTERNAL_NAMES`) are never touched.
- A Lookup field with no resolvable lookup list, or a Managed Metadata field
  with no resolvable term set (or a term set that resolves to zero terms),
  shows as "Populated? = No" rather than erroring the whole batch.
- If a list has more than one assignable (non-hidden, non-Folder) content
  type, one is randomly assigned per item - same as the C# tool.
- Calculated/Computed fields, File/Attachments, and any other unrecognized
  field type are left alone.

## What's different from the C# original
- **Auth**: the C# tool uses PnP PowerShell's old cookie-based "web login"
  popup (no Azure AD app registration needed). This uses the same
  MSAL-interactive-browser flow every other script in this workspace
  already uses via `sharepoint.connect()` - a different, but equally
  interactive, sign-in experience.
- **Schema reading**: Office365-REST-Python-Client returns a field's full set
  of type-specific REST properties (Choices, LookupList, TermSetId, etc.) in
  a single response, unlike CSOM, which needs a separate `CastTo<T>()` +
  `Include()` round-trip per field type. `schema_reader.py` reads everything
  it needs in one `ctx.load()`/`execute_query()` call.
- **Randomness**: uses Python's `Faker` library in place of the C# tool's
  `Bogus` - similar idea (realistic fake text/dates/numbers), different
  library, so exact generated values won't match between the two tools.

## Tested
Every module was verified against mock data (no live SharePoint connection
required for this, since interactive sign-in needs your real credentials):
- `schema_reader.get_writable_fields()`: verified that hidden fields,
  read-only fields, and skip-listed internal names are excluded; that a
  Lookup field with an empty `LookupList` and a Taxonomy field with an empty
  `TermSetId` both correctly come back `is_supported=False`.
- `value_generator.DummyValueGenerator`: verified every one of the 15
  supported field-kind handlers (Text, Note, Choice, MultiChoice, Number,
  Currency, Boolean, DateTime date-only/date-time, URL, Guid, Geolocation,
  User single/multi, Lookup single/multi, Taxonomy single/multi) produces a
  value of the correct type/shape, and that each correctly returns
  `UNSUPPORTED` when its reference data (no site users, no lookup
  candidates, no terms, empty choice list) is unavailable.
- `item_creator.create_items()`: verified batch-flush timing (e.g. 25 items
  at batch size 10 → exactly 3 `execute_query()` calls, progress reported as
  `[10, 20, 25]`), and that `ContentTypeId` is randomly assigned across both
  values when a list has more than one assignable content type.
- The GUI itself: verified headlessly (widget wiring, default values, the
  fields grid populating from schema data, and all three `_on_generate()`
  validation guards - no list selected, no populatable fields, non-numeric
  item count/batch size).

**Not verified**: the actual Connect → pick list → Generate flow against a
real tenant - that needs your real Microsoft 365 credentials via interactive
browser sign-in, which I have no way to complete myself. Please run it
yourself against a real (ideally test/dev) list and confirm the generated
items look right, especially the Lookup/Person/Managed Metadata fields,
since those depend on your tenant's actual data.

## Logging
No separate log file - status messages (connect progress, field counts,
generation progress) appear in the in-app text panel only, same as
[SharePoint Explorer](../SharePointExplorer/README.md).

## Status
- [x] All four modules (`schema_reader`, `value_generator`, `item_creator`,
  the GUI) verified against mock data / headlessly - see Tested above
- [ ] **Full interactive flow against a real list - untested, please verify
  yourself, especially Lookup/Person/Managed Metadata output**
