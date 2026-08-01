"""
SYNOPSIS
    Gets current weather plus a multi-day forecast for any location by name -
    no API key required. Looks up coordinates via Open-Meteo's free geocoding
    API, then fetches current conditions and a daily forecast for those
    coordinates from Open-Meteo's free forecast API. Provides logging (with
    daily log rotation, retention, and per-run CorrelationID), module
    dependency checking, and error handling.

DESCRIPTION
    Copy this file as the starting point for a new script, then:
    - Update REQUIRED_MODULES if you depend on different packages
    - Update default args (e.g. --location, --forecast-days) for typical usage
    - Adjust WEATHER_CODE_DESCRIPTIONS if you want different wording

EXAMPLE
    python get_weather.py --location "Zurich"
    python get_weather.py --location "New York" --units imperial
    python get_weather.py --location "Zurich" --forecast-days 5

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-07-30
    Modified by : Ruchik Shah
    Modified on : 2026-07-30
    Version     : 1.1.0
"""

import argparse
import importlib
import logging
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

#region Module Dependency Check
REQUIRED_MODULES = ["requests"]

for module_name in REQUIRED_MODULES:
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"Required module '{module_name}' is not installed. Install it with: pip install {module_name}")
        sys.exit(1)

import requests
#endregion

#region Global Variables
SCRIPT_FOLDER = Path(__file__).resolve().parent
LOGS_DIRECTORY = SCRIPT_FOLDER / "Logs"
LOG_FILE_NAME = LOGS_DIRECTORY / f"get_weather_{datetime.now():%Y%m%d}.log"
PURGE_LOG_DAYS = 7

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes, as used by Open-Meteo -
# see https://open-meteo.com/en/docs for the full table.
WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

CORRELATION_ID = str(uuid.uuid4())[:11]
#endregion

#region Logging Setup
def check_log_directory():
    LOGS_DIRECTORY.mkdir(parents=True, exist_ok=True)


def delete_old_logs(logger):
    if PURGE_LOG_DAYS <= 0:
        return
    try:
        logger.info("Deleting log files older than %s days", PURGE_LOG_DAYS)
        cutoff = datetime.now() - timedelta(days=PURGE_LOG_DAYS)
        for log_file in LOGS_DIRECTORY.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
        logger.info("Log files deleted")
    except Exception as ex:
        logger.error("Error deleting log files. Details: %s", ex)


def get_logger():
    logger = logging.getLogger("get_weather")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
#endregion


DAILY_FIELDS = "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", required=True, help='Place name, e.g. "Zurich" or "New York"')
    parser.add_argument("--units", choices=["metric", "imperial"], default="metric")
    parser.add_argument("--forecast-days", type=int, default=5, help="Number of days to forecast, including today")
    return parser.parse_args()


def geocode_location(location_name, logger):
    """Returns (latitude, longitude, resolved_name, country) for a place name,
    using Open-Meteo's free geocoding API (no API key needed)."""
    logger.info("Looking up coordinates for '%s'", location_name)
    response = requests.get(GEOCODING_URL, params={"name": location_name, "count": 1})
    response.raise_for_status()
    results = response.json().get("results")

    if not results:
        raise ValueError(f"Location '{location_name}' not found")

    match = results[0]
    return match["latitude"], match["longitude"], match["name"], match.get("country")


def get_weather_data(latitude, longitude, temperature_unit, windspeed_unit, forecast_days, logger):
    """Returns (current_weather dict, daily forecast dict) for the given
    coordinates in a single call, using Open-Meteo's free forecast API
    (no API key needed). The daily dict has parallel lists keyed by field
    name, e.g. daily["time"][0] pairs with daily["temperature_2m_max"][0]."""
    logger.info("Fetching weather for (%s, %s), %s day(s)", latitude, longitude, forecast_days)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "daily": DAILY_FIELDS,
        "temperature_unit": temperature_unit,
        "windspeed_unit": windspeed_unit,
        "timezone": "auto",
        "forecast_days": forecast_days,
    }
    response = requests.get(FORECAST_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data["current_weather"], data["daily"]


def main_process(args, logger):
    temperature_unit = "celsius" if args.units == "metric" else "fahrenheit"
    windspeed_unit = "kmh" if args.units == "metric" else "mph"
    temp_symbol = "C" if args.units == "metric" else "F"
    speed_unit = "km/h" if args.units == "metric" else "mph"

    latitude, longitude, resolved_name, country = geocode_location(args.location, logger)
    logger.info("Resolved '%s' to %s, %s (%s, %s)", args.location, resolved_name, country, latitude, longitude)

    current, daily = get_weather_data(
        latitude, longitude, temperature_unit, windspeed_unit, args.forecast_days, logger
    )

    description = WEATHER_CODE_DESCRIPTIONS.get(current["weathercode"], "Unknown")
    logger.info("--- Current ---")
    logger.info("Time: %s", current["time"])
    logger.info("Temperature: %s%s", current["temperature"], temp_symbol)
    logger.info("Wind: %s %s from %s degrees", current["windspeed"], speed_unit, current["winddirection"])
    logger.info("Condition: %s", description)

    logger.info("--- %s-day forecast ---", args.forecast_days)
    for date, code, temp_max, temp_min, wind_max in zip(
        daily["time"], daily["weathercode"], daily["temperature_2m_max"],
        daily["temperature_2m_min"], daily["windspeed_10m_max"],
    ):
        day_description = WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")
        logger.info(
            "%s: %s | High %s%s / Low %s%s | Wind up to %s %s",
            date, day_description, temp_max, temp_symbol, temp_min, temp_symbol, wind_max, speed_unit,
        )


def main():
    args = parse_args()
    check_log_directory()
    logger = get_logger()

    script_start_time = datetime.now()
    stopwatch_start = time.perf_counter()

    try:
        delete_old_logs(logger)
        logger.info("=" * 64)
        logger.info("Script started at %s (CorrelationID: %s)", script_start_time, CORRELATION_ID)

        main_process(args, logger)

        elapsed = time.perf_counter() - stopwatch_start
        logger.info("Script finished at %s, time taken: %.3fs (CorrelationID: %s)",
                     datetime.now(), elapsed, CORRELATION_ID)
        logger.info("=" * 64)
    except Exception as ex:
        elapsed = time.perf_counter() - stopwatch_start
        logger.error("Script failed at %s, time taken: %.3fs (CorrelationID: %s). Details: %s",
                     datetime.now(), elapsed, CORRELATION_ID, ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
