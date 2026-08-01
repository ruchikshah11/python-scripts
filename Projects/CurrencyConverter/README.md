# Currency Converter

Converts an amount between currencies using the free [Frankfurter](https://frankfurter.dev)
API (European Central Bank reference rates) — **no API key required**.

## Prerequisites
```
pip install requests
```

## Run it
```
python convert_currency.py --amount 100 --from-currency USD --to-currency EUR
python convert_currency.py --list-currencies
```
Defaults: `--amount 1`, `--from-currency USD`, `--to-currency EUR`.

## Output
- Normal conversion: date, `<amount> <FROM> = <converted> <TO>`, and the implied rate
- `--list-currencies`: every supported 3-letter currency code + full name

## Edge cases (tested live)
- **Same currency** (e.g. USD → USD): Frankfurter's API rejects this pair with a 422 error,
  so the script handles it directly and returns the amount unchanged at rate 1.0, without
  calling the API.
- **Invalid currency code** (e.g. XXX): Frankfurter returns 404 "not found" — surfaced as a
  clear error message, exit code 1.
- A couple of currency names (Polish Złoty, Icelandic Króna) contain accented characters
  that may display garbled in a Windows console depending on its codepage — this is a
  terminal display limitation, not a bug; the underlying data and log file are correct UTF-8.

## Logging
Logs are written to `Logs/convert_currency_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (tested live: normal conversion, same-currency, invalid
  currency, and --list-currencies)
