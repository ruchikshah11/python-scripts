# Email Template Generator

Generates the bs one QM bilingual (German + English) email notification templates -
one HTML file per notification type, matching the approved design (right-aligned
**bs one: Qualität** header, white card with a German block, a divider, then an
English block, and a bilingual footer).

The original PnP-provisioned HTML files under bsone.deployment.qm's
`ProvisioningTemplates/EmailTemplates/Files/English` and `.../German` folders ship
with no body content at all (just a `<title>`, no markup) - only the subject lines
exist, in the two PnP provisioning XML manifests (`bsone-QM-EmailTemplates-ContentEN.xml`
/ `ContentDE.xml`). This script hard-codes, per template, those subject lines plus
hand-authored DE/EN body copy (drafted from the template's name and subject, since no
source body copy exists anywhere), and renders each one through a single shared HTML
shell so every output file is visually consistent.

Output is one **combined bilingual file per notification type** (not separate EN/DE
files) written to `Files/Combined/<TemplateName>.html`.

## Prerequisites
None beyond the standard library.

## Run it
```
python generate_email_templates.py
python generate_email_templates.py --out-dir "C:/some/other/folder"
```
Default output folder:
`C:\Ruchik\BSTFS\bsone.deployment.qm\2_Packages\QM\ProvisioningTemplates\EmailTemplates\Files\Bilingual`

## IMPORTANT - do not restructure the HTML
The `SHELL` template (outer table layout, header, white card, DE/EN block order,
divider, footer markup) is the **approved design** - do not change its structure.
Only the `TEMPLATES` data (subject lines / body copy) is meant to be edited freely.
If wording needs to change, edit the relevant `body_*` function or `TEMPLATES` entry,
not the shell.

## How it works
1. `TEMPLATES` is a dict keyed by template filename (no extension), each holding
   `subject_en`, `subject_de`, and a `body` tuple `(en_html, de_html)` built by one of
   the `body_*` helper functions (e.g. `body_review_task`, `body_deletion_notify`).
2. The `body_*` helpers take a `DOC` or `PROC` entity dict (holding the linked
   `[DocumentName] ([DocumentNumber])` / `[ProcessName] ([ProcessNumber])` markup and
   the German grammatical forms - nominative/accusative/genitive - needed for correct
   phrasing) and return ready-to-embed HTML paragraph fragments.
3. `main_process()` fills the `SHELL` with each template's `de_body`/`en_body`, runs
   it through `indent_html()` (a small post-processing pass that nests each line by
   tracking `<table>`/`<tr>`/`<td>`/`<html>`/`<head>`/`<body>` depth - whitespace
   only, never touches the tags themselves), and writes the result to `--out-dir`.

## Tested
Ran end-to-end against the real target folder: generated all 81 templates, verified
`bsoneQMDocumentReviewTask.html` renders identically to the approved design screenshot,
and confirmed every generated `<p>`/field line sits on its own line (not concatenated).

## Logging
Logs are written to `Logs/generate_email_templates_<date>.log`, with a per-run
CorrelationID and 7-day retention - same pattern as
[ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end: 81/81 templates generated, output matches the
  approved design, formatting confirmed one element per line.
