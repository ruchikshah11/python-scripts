"""
SYNOPSIS
    A Tkinter desktop weather app with a clean, card-style UI - built for end
    users rather than the terminal. Reuses get_weather.py's tested functions
    directly (geocode_location, get_weather_data, WEATHER_CODE_DESCRIPTIONS) -
    no weather logic is duplicated here, this file only adds the visual layer.

DESCRIPTION
    Enter a location, pick metric/imperial, and press Search (or just launch
    the app - it loads your last-used location by default). Shows a big
    "hero" card with the current temperature, condition icon, and wind, plus
    a row of forecast cards for the next few days. The hero card's background
    color and icon change with the condition (sunny/cloudy/rainy/snowy/stormy).
    The network call runs on a background thread so the window never freezes.
    The currently-displayed location refreshes itself automatically every 5
    minutes (AUTO_REFRESH_INTERVAL_MS) so the temperature/condition stay
    current without needing to press Search again.

EXAMPLE
    python weather_app.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-01
    Modified by : Ruchik Shah
    Modified on : 2026-08-01
    Version     : 1.1.0
"""

import json
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

SCRIPT_FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_FOLDER))

import get_weather  # noqa: E402 - reuse the tested CLI script's functions directly

DEFAULT_LOCATION = "Zurich"
FORECAST_DAYS = 5
AUTO_REFRESH_INTERVAL_MS = 5 * 60 * 1000  # re-fetch the current location every 5 minutes

SETTINGS_FILE = SCRIPT_FOLDER / "weather_settings.json"


def load_settings():
    """Returns the last-used {location, country, units}, or the defaults if
    no settings file exists yet (first run) or it can't be read."""
    defaults = {"location": DEFAULT_LOCATION, "country": "", "units": "metric"}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as settings_file:
            saved = json.load(settings_file)
        defaults.update({key: saved[key] for key in defaults if key in saved})
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


def save_settings(location, country, units):
    """Persists the values that made a search succeed, so they're prefilled
    as defaults the next time the app is launched."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
        json.dump({"location": location, "country": country, "units": units}, settings_file)

# (icon, accent background, accent foreground) per weather-code group -
# grouped the same way get_weather.WEATHER_CODE_DESCRIPTIONS documents them.
CONDITION_VISUALS = {
    "clear": ("☀", "#F5A623", "#2B2000"),          # sun
    "cloudy": ("⛅", "#8D99AE", "#1B1F27"),          # sun behind cloud
    "overcast": ("☁", "#6C7A89", "#F4F6F7"),        # cloud
    "fog": ("\U0001F32B", "#B0B7C6", "#20242C"),         # fog
    "rain": ("\U0001F327", "#4A7FBF", "#F4F6F7"),        # rain cloud
    "snow": ("❄", "#AFD9E8", "#0F2A38"),            # snowflake
    "storm": ("⛈", "#5B4B8A", "#F4F6F7"),           # thunder cloud
}


def classify_weather_code(code):
    """Groups an Open-Meteo WMO weather code into one of CONDITION_VISUALS'
    keys, returning (icon, background, foreground) for that group."""
    if code == 0:
        group = "clear"
    elif code in (1, 2):
        group = "cloudy"
    elif code == 3:
        group = "overcast"
    elif code in (45, 48):
        group = "fog"
    elif code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        group = "rain"
    elif code in (71, 73, 75, 77, 85, 86):
        group = "snow"
    elif code in (95, 96, 99):
        group = "storm"
    else:
        group = "overcast"
    return CONDITION_VISUALS[group]


def geocode_location_in_country(location_name, country_text, logger):
    """Like get_weather.geocode_location, but when country_text is given
    (free text, e.g. "US" or "United States"), prefers whichever of the top
    10 matches is actually in that country - lets the Country box disambiguate
    same-named places (e.g. "Springfield") instead of always taking
    Open-Meteo's top-ranked match. Matches case-insensitively against either
    the result's ISO country code or its full country name."""
    logger.info("Looking up coordinates for '%s' (country filter: %s)", location_name, country_text or "any")
    response = get_weather.requests.get(
        get_weather.GEOCODING_URL, params={"name": location_name, "count": 10}
    )
    response.raise_for_status()
    results = response.json().get("results")

    if not results:
        raise ValueError(f"Location '{location_name}' not found")

    if not country_text:
        match = results[0]
    else:
        needle = country_text.strip().lower()
        match = next((
            candidate for candidate in results
            if needle == (candidate.get("country_code") or "").lower()
            or needle == (candidate.get("country") or "").lower()
        ), None)
        if match is None:
            raise ValueError(f"'{location_name}' not found in country '{country_text}'")

    return match["latitude"], match["longitude"], match["name"], match.get("country")


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather")
        self.root.geometry("420x640")
        self.root.minsize(380, 560)
        self._closed = False
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        get_weather.check_log_directory()
        self.logger = get_weather.get_logger()

        style = ttk.Style()
        style.configure("Toolbutton", padding=(10, 4))

        self.settings = load_settings()

        self._build_search_bar()

        self.hero_frame = tk.Frame(self.root, bg="#8D99AE")
        self.hero_frame.pack(fill="x", padx=0, pady=0)
        self._build_hero_card()

        self.status_label = ttk.Label(self.root, text="", foreground="#B00020")
        self.status_label.pack(fill="x", padx=12, pady=(4, 0))

        self.forecast_container = ttk.Frame(self.root)
        self.forecast_container.pack(fill="both", expand=True, padx=8, pady=8)

        self.updated_label = ttk.Label(self.root, text="", font=("Segoe UI", 8), foreground="#888888")
        self.updated_label.pack(fill="x", padx=12, pady=(0, 6))

        self._set_loading(False)
        self._fetch_weather(self.settings["location"], self.settings["units"], self.settings["country"])
        self._schedule_auto_refresh()

    def _on_close(self):
        self._closed = True
        self.root.destroy()

    def _schedule_auto_refresh(self):
        if self._closed:
            return
        self.root.after(AUTO_REFRESH_INTERVAL_MS, self._auto_refresh)

    def _auto_refresh(self):
        if self._closed:
            return
        self.logger.info("Auto-refreshing weather for '%s'", self.last_location)
        self._fetch_weather(self.last_location, self.last_units, self.last_country, silent=True)
        self._schedule_auto_refresh()

    # ---------- layout ----------

    def _build_search_bar(self):
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=10, pady=10)
        bar.columnconfigure(0, weight=1)

        self.location_entry = ttk.Entry(bar, font=("Segoe UI", 11))
        self.location_entry.insert(0, self.settings["location"])
        self.location_entry.grid(row=0, column=0, columnspan=4, sticky="ew", ipady=3)
        self.location_entry.bind("<Return>", lambda event: self._on_search())

        self.country_entry = ttk.Entry(bar, font=("Segoe UI", 10))
        self.country_entry.insert(0, self.settings["country"])
        self._set_placeholder_if_empty(self.country_entry, "Country (optional)")
        self.country_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.country_entry.bind("<Return>", lambda event: self._on_search())

        self.units = tk.StringVar(value=self.settings["units"])
        ttk.Radiobutton(bar, text="°C", variable=self.units, value="metric",
                         style="Toolbutton").grid(row=1, column=1, padx=(6, 0), pady=(6, 0))
        ttk.Radiobutton(bar, text="°F", variable=self.units, value="imperial",
                         style="Toolbutton").grid(row=1, column=2, padx=(4, 0), pady=(6, 0))

        ttk.Button(bar, text="Search", command=self._on_search).grid(row=1, column=3, padx=(6, 0), pady=(6, 0))

    def _set_placeholder_if_empty(self, entry, placeholder):
        """Shows greyed-out placeholder text in an empty Entry (Tkinter has
        no native placeholder support) - clears automatically on first edit."""
        if entry.get():
            return
        entry.insert(0, placeholder)
        entry.configure(foreground="#888888")

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.configure(foreground="")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground="#888888")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _build_hero_card(self):
        self.icon_label = tk.Label(self.hero_frame, text="", font=("Segoe UI Emoji", 56),
                                     bg=self.hero_frame["bg"])
        self.icon_label.pack(pady=(18, 0))

        self.temp_label = tk.Label(self.hero_frame, text="", font=("Segoe UI", 48, "bold"),
                                     bg=self.hero_frame["bg"])
        self.temp_label.pack()

        self.condition_label = tk.Label(self.hero_frame, text="", font=("Segoe UI", 14),
                                          bg=self.hero_frame["bg"])
        self.condition_label.pack()

        self.place_label = tk.Label(self.hero_frame, text="", font=("Segoe UI", 12, "bold"),
                                      bg=self.hero_frame["bg"])
        self.place_label.pack(pady=(8, 0))

        self.wind_label = tk.Label(self.hero_frame, text="", font=("Segoe UI", 10),
                                     bg=self.hero_frame["bg"])
        self.wind_label.pack(pady=(2, 18))

    def _paint_hero(self, background, foreground):
        self.hero_frame.configure(bg=background)
        for widget in (self.icon_label, self.temp_label, self.condition_label,
                       self.place_label, self.wind_label):
            widget.configure(bg=background, fg=foreground)

    def _build_forecast_card(self, parent, date_text, code, temp_max, temp_min, temp_symbol):
        icon, background, foreground = classify_weather_code(code)
        day_name = datetime.strptime(date_text, "%Y-%m-%d").strftime("%a")

        card = tk.Frame(parent, bg=background, highlightthickness=0)
        tk.Label(card, text=day_name, font=("Segoe UI", 10, "bold"),
                 bg=background, fg=foreground).pack(pady=(8, 0))
        tk.Label(card, text=icon, font=("Segoe UI Emoji", 22), bg=background).pack()
        tk.Label(card, text=f"{round(temp_max)}°{temp_symbol}", font=("Segoe UI", 11, "bold"),
                 bg=background, fg=foreground).pack()
        tk.Label(card, text=f"{round(temp_min)}°{temp_symbol}", font=("Segoe UI", 10),
                 bg=background, fg=foreground).pack(pady=(0, 8))
        return card

    # ---------- state ----------

    def _set_loading(self, is_loading):
        state = "disabled" if is_loading else "normal"
        self.location_entry.configure(state=state)
        self.status_label.configure(text="Loading..." if is_loading else "")

    def _show_error(self, message):
        self.status_label.configure(text=message)

    # ---------- events ----------

    def _on_search(self):
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showwarning("Weather", "Enter a location first")
            return
        country = self._country_entry_value()
        self._fetch_weather(location, self.units.get(), country)

    def _country_entry_value(self):
        text = self.country_entry.get().strip()
        return "" if text == "Country (optional)" else text

    def _fetch_weather(self, location, units, country, silent=False):
        self.last_location, self.last_units, self.last_country = location, units, country

        if not silent:
            self._set_loading(True)

        def task():
            try:
                temperature_unit = "celsius" if units == "metric" else "fahrenheit"
                windspeed_unit = "kmh" if units == "metric" else "mph"
                temp_symbol = "C" if units == "metric" else "F"
                speed_unit = "km/h" if units == "metric" else "mph"

                latitude, longitude, resolved_name, resolved_country = geocode_location_in_country(
                    location, country, self.logger
                )
                current, daily = get_weather.get_weather_data(
                    latitude, longitude, temperature_unit, windspeed_unit, FORECAST_DAYS, self.logger
                )

                save_settings(location, country, units)
                if self._closed:
                    return
                self.root.after(0, self._on_weather_loaded, current, daily,
                                 resolved_name, resolved_country, temp_symbol, speed_unit)
            except Exception as ex:
                self.logger.error("Weather lookup failed: %s", ex)
                if self._closed:
                    return
                self.root.after(0, self._on_weather_failed, str(ex), silent)

        threading.Thread(target=task, daemon=True).start()

    def _on_weather_failed(self, message, silent=False):
        self._set_loading(False)
        if silent:
            # A silent auto-refresh failure (e.g. a transient network hiccup)
            # shouldn't overwrite whatever the user is currently looking at -
            # it's already logged to file, and the next refresh will retry.
            self.logger.error("Auto-refresh failed silently: %s", message)
        else:
            self._show_error(f"Couldn't load weather: {message}")

    def _on_weather_loaded(self, current, daily, resolved_name, country, temp_symbol, speed_unit):
        self._set_loading(False)
        self._show_error("")
        self.updated_label.configure(text=f"Updated {datetime.now():%I:%M:%S %p}")

        icon, background, foreground = classify_weather_code(current["weathercode"])
        description = get_weather.WEATHER_CODE_DESCRIPTIONS.get(current["weathercode"], "Unknown")

        self._paint_hero(background, foreground)
        self.icon_label.configure(text=icon)
        self.temp_label.configure(text=f"{round(current['temperature'])}°{temp_symbol}")
        self.condition_label.configure(text=description)
        place_text = f"{resolved_name}, {country}" if country else resolved_name
        self.place_label.configure(text=place_text)
        self.wind_label.configure(
            text=f"Wind {current['windspeed']} {speed_unit} • {current['time']}"
        )

        for child in self.forecast_container.winfo_children():
            child.destroy()

        for index, (date_text, code, temp_max, temp_min) in enumerate(zip(
            daily["time"], daily["weathercode"],
            daily["temperature_2m_max"], daily["temperature_2m_min"],
        )):
            card = self._build_forecast_card(self.forecast_container, date_text, code,
                                              temp_max, temp_min, temp_symbol)
            card.grid(row=0, column=index, sticky="nsew", padx=4)
            self.forecast_container.columnconfigure(index, weight=1)


def main():
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
