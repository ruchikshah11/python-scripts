# Get Weather

Gets current weather plus a multi-day forecast for any location by name — **no API
key required**. Looks up coordinates via [Open-Meteo](https://open-meteo.com)'s free
geocoding API, then fetches current conditions and a daily forecast for those
coordinates from Open-Meteo's free forecast API (one combined call).

Your existing [Get-Weather.ps1](../../../../../../Ruchik/PowerShell/Utilities/Integrations/Weather/Weather%20App/Get-Weather.ps1)
uses OpenWeatherMap's numeric City ID system, which needs a free account + API key.
This script deliberately uses Open-Meteo instead, trading "numeric location ID" for
"plain location name" in exchange for zero signup/key management.

## Prerequisites
```
pip install requests
```

## Run it
```
python get_weather.py --location "Zurich"
python get_weather.py --location "New York" --units imperial
python get_weather.py --location "Zurich" --forecast-days 3
```
`--forecast-days` defaults to 5 and includes today as day 1.

## Output
Resolved location name/country/coordinates, then:
- **Current**: time, temperature, wind speed/direction, plain-language condition
- **N-day forecast**: one line per day — date, condition, high/low temperature, max wind speed

Conditions are mapped from Open-Meteo's WMO weather code table.

## Errors
- Unknown location name → clear "Location '...' not found" error, exit code 1
- Network/API failures surface via `requests`' exceptions, logged and exit code 1

## Logging
Logs are written to `Logs/get_weather_<date>.log`, with a per-run CorrelationID and
7-day retention — same pattern as [ScriptTemplate.py](../../Utilities/Templates/ScriptTemplate/ScriptTemplate.py).

## Status
- [x] Verified working end-to-end (tested live: Zurich metric 5-day, New York imperial
  3-day, and an invalid-location error case)

---

# Weather App (GUI)

A Tkinter desktop version for end users who'd rather not use the command line.
Reuses `get_weather.py`'s functions directly (`geocode_location`, `get_weather_data`,
`WEATHER_CODE_DESCRIPTIONS`) — the CLI script above is untouched, this is a separate
file that adds a visual layer on top of it.

## Run it
```
python weather_app.py
```
Loads your last-used location/country/units by default (Zurich/metric on first
run). Type a location, optionally type a **Country** (name or code, e.g. "US" or
"United States") to disambiguate same-named places (e.g. "Springfield" exists in
several US states), then press **Search** (or Enter). Toggle °C/°F with the
segmented buttons next to it.

Whatever location/country/units you last searched with successfully is saved to
`weather_settings.json` next to this script and prefilled the next time you
launch the app.

## Look and feel
- A "hero" card shows the current temperature, an icon, condition text, resolved
  place name, and wind — its background/text color changes with the condition
  (sunny = amber, cloudy/overcast = gray, rain = blue, snow = pale blue, storm =
  purple), using the same WMO weather codes `get_weather.py` already maps.
- Below it, a row of small forecast cards (one per day, 5 by default) each with
  day-of-week, icon, and high/low.
- A small "Updated HH:MM:SS" line under the forecast shows when the data was
  last refreshed.
- The API call runs on a background thread (same pattern as the other GUIs in this
  workspace) so the window never freezes while it loads.

## Auto-refresh
The currently-shown location re-fetches itself automatically every 5 minutes
(`AUTO_REFRESH_INTERVAL_MS`) so the temperature/condition stay current without
needing to press Search again — useful if you leave the app open. Auto-refresh
runs silently: it doesn't disable the search box or show "Loading...", and if a
refresh fails (e.g. a transient network hiccup) it's logged rather than shown as
an error, so a single dropped background refresh doesn't disrupt whatever you're
looking at. Every successful refresh (manual or automatic) updates the
"Updated HH:MM:SS" line.

## Tested
Verified the full data path this UI depends on, live: geocoding "Zurich",
fetching current + 5-day forecast, and classifying every returned weather code
(including a thunderstorm code that came back on test day) to a valid icon/color
pair with no errors. Also compiled cleanly and ran `classify_weather_code()`
against all 28 documented WMO codes plus an unknown one, confirming no code falls
through without a valid icon/color. Free-text country matching was verified live
against both an ISO code ("US") and a full name ("United States"), a non-matching
country correctly raises a clear error, and settings persistence (save/load,
including a corrupted settings file falling back to defaults) was unit-tested.
Auto-refresh was verified live end-to-end with a real Tkinter `mainloop()`
running: the initial load populated the hero card and "Updated" timestamp, and a
manually-triggered refresh repopulated everything again with a fresh timestamp.

**Not verified**: the actual rendered layout/spacing and emoji glyph rendering —
I have no screenshot capability, so please launch it yourself to confirm it looks
right on your machine. Also not verified: behavior across the *real* 5-minute
interval (I tested the refresh logic directly rather than waiting 5 real minutes).

## Logging
Uses `get_weather.py`'s same logger/log file (`Logs/get_weather_<date>.log`) — no
separate log file for the GUI.

## Status
- [x] Data pipeline (geocode + forecast + condition classification) verified live
- [ ] Visual layout/emoji rendering — please confirm it looks right, I can't see
  it myself
