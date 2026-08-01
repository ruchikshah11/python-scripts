# QR Code Generator

Generates a QR code image (PNG) encoding any text or URL.

## Prerequisites
```
pip install qrcode[pil]
```

## Run it
```
python generate_qr.py --data "https://github.com" --output qr.png
python generate_qr.py --data "Hello World" --output hello.png --box-size 12
```
`--box-size` (default 10) controls the pixel size per QR module; `--border` (default 4,
the spec minimum) controls the quiet-zone width.

## Output
Logs the number of characters encoded, the QR version chosen automatically to fit that
data, and the save path.

## Tested
Generated a QR code for `https://github.com`, verified the output is a valid PNG
(`Pillow` confirmed format/size), then **decoded it back** with `pyzbar` — the decoded
content matched `https://github.com` exactly, confirming a genuine round-trip, not
just "the library probably works."

## Logging
Logs are written to `Logs/generate_qr_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (generated, confirmed valid PNG, decoded back
  successfully with matching content)
