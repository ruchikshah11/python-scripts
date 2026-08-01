# Report Builder

Builds a formatted PDF or Excel report from a CSV file — output format is inferred
from the `--output` file extension (`.xlsx` or `.pdf`).

## Prerequisites
```
pip install openpyxl reportlab
```

## Run it
```
python build_report.py --input data.csv --output report.xlsx
python build_report.py --input data.csv --output report.pdf --title "Sales Report"
```

## Output
- **Title** at the top (merged/centered in Excel, styled paragraph in PDF)
- **Header row** with a blue background and white bold text
- **Data rows** below, in a bordered table (alternating row shading in the PDF)
- **Excel-only**: auto-sized column widths based on content, frozen header row
- **PDF-only**: landscape orientation, header row repeats if the table spans pages

## Errors
- Missing input file → clear error, exit code 1
- Empty CSV → clear error, exit code 1
- Unsupported `--output` extension (anything but `.xlsx`/`.pdf`) → clear error,
  exit code 1

## Tested
Verified against a 4-row sample CSV (Name/Department/Score): both `.xlsx` and `.pdf`
generated successfully. Confirmed by reading the `.xlsx` back with `openpyxl` — title,
header, and all 4 data rows matched the source exactly — and checking the `.pdf`'s
file signature (`%PDF-1.4`). Both error cases (missing input, unsupported extension)
also verified.

## Logging
Logs are written to `Logs/build_report_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (Excel content verified by reading it back, PDF
  signature verified, both error cases tested)
