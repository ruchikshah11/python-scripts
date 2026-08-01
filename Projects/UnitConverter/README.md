# Unit Converter

Converts a value between units of length, weight, or temperature.

## Prerequisites
None beyond the standard library.

## Run it
```
python convert_units.py --category length --value 5 --from-unit mi --to-unit km
python convert_units.py --category weight --value 1 --from-unit kg --to-unit lb
python convert_units.py --category temperature --value 100 --from-unit C --to-unit F
python convert_units.py --category length --list-units
```

## Units
| Category | Units |
|---|---|
| `length` | mm, cm, m, km, in, ft, yd, mi |
| `weight` | mg, g, kg, oz, lb |
| `temperature` | C, F, K |

Length/weight are simple linear conversions via a shared base unit (meters/grams).
Temperature uses proper formulas (not a linear factor), normalizing through Celsius.

## Errors
- Unknown unit for the given category → clear error listing valid units, exit code 1
- Missing `--value`/`--from-unit`/`--to-unit` (when not using `--list-units`) → clear
  error, exit code 1

## Tested
Verified against known-correct conversions: 5 mi → 8.04672 km, 1 kg → 2.204623 lb,
100°C → 212°F, 0°C → 273.15 K, and the famous -40°F = -40°C crossover point. Also
tested `--list-units` and an invalid-unit error case.

## Logging
Logs are written to `Logs/convert_units_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (all conversions checked against known-correct
  values, list-units, and invalid-unit error)
