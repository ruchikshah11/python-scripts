# Email Template Manifest Generator

Generates the PnP provisioning XML manifest for the bs one QM **combined** (bilingual,
DE / EN) email templates - one `<pnp:File>` entry per template, pointing at
`Files/Combined/<TemplateName>.html`.

The two original manifests (`bsone-QM-EmailTemplates-ContentEN.xml` and `ContentDE.xml`,
in the deployment repo) each list one entry per language per template, with a
single-language `bsoneSubject` and a `bsoneLanguage` taxonomy field. Now that every
notification type is a single combined bilingual HTML file (see the
[EmailTemplateGenerator](../EmailTemplateGenerator/README.md) project), those two
manifests no longer describe reality on their own, so this script produces a third,
separate manifest for the combined set:

| Property | Value |
|---|---|
| `Src` | `.\Files\Combined\<TemplateName>.html` |
| `Title` | same key as before, e.g. `bsoneQMDocumentReviewTask` |
| `bsoneSubject` | `"<German subject> / <English subject>"` - German first, matching the body's DE-then-EN order |
| `bsoneLanguage` | dropped entirely - the item is no longer single-language |
| `bsonePowerAutomateDetails` | kept where the original manifests had it, combined the same `"DE / EN"` way when the two languages' text actually differed |

**Never hard-codes or duplicates any subject text.** Every subject and
`bsonePowerAutomateDetails` value is parsed straight out of `ContentEN.xml` /
`ContentDE.xml` each run, matched by `Title`. So when someone adds or edits a template
in those two manifests - the normal, existing workflow - re-running this script alone
picks it up. No script edits, ever, for a new or changed subject. A `Title` present in
only one of the two source files is skipped with a warning (both languages are needed
for a combined bilingual entry).

The old `ContentEN.xml` / `ContentDE.xml` are left untouched - this only reads them and
writes a separate, additional file.

## Prerequisites
None beyond the standard library.

## Run it
```
python generate_combined_manifest.py
python generate_combined_manifest.py --xml-path "C:/some/other/manifest.xml"
python generate_combined_manifest.py --en-path "C:/.../ContentEN.xml" --de-path "C:/.../ContentDE.xml"
```
Default output:
`C:\Ruchik\BSTFS\bsone.deployment.qm\2_Packages\QM\ProvisioningTemplates\EmailTemplates\bsone-QM-EmailTemplates-ContentCombined.xml`

## Tested
Ran against the real target: parsed 81 entries from each source manifest, wrote 81
`<pnp:File>` entries (5 carrying `bsonePowerAutomateDetails`), verified `Src` paths
point at `Files\Combined\`, subjects read `"<DE> / <EN>"`, and no `bsoneLanguage`
property appears anywhere in the output. Also verified against synthetic manifests
with a title present in only one language - correctly skipped with a warning, not
silently dropped or crashed.

## Logging
Logs are written to `Logs/generate_combined_manifest_<date>.log`, with a per-run
CorrelationID and 7-day retention - same pattern as
[ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end against the real target folder: 81/81 entries
  generated correctly, existing scripts left untouched.
