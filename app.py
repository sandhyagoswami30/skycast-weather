from __future__ import annotations

import os
from typing import Any

import requests
from flask import Flask, flash, render_template, request

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-key-change-before-deploy")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 12


class WeatherLookupError(Exception):
    """A user-friendly error while looking up a location or forecast."""


def find_location(city: str, district: str, state: str, country: str) -> dict[str, Any]:
    """Find a likely location worldwide, preferring matching region/district results."""
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": f"{city}, {state}, {country}",
                "count": 10,
                "language": "en",
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
    except (requests.RequestException, ValueError) as exc:
        raise WeatherLookupError("The location service is unavailable right now. Please try again.") from exc

    if not results:
        raise WeatherLookupError("We couldn't find that city. Check the spelling and try again.")

    state_key = state.casefold().strip()
    district_key = district.casefold().strip()

    def score(location: dict[str, Any]) -> int:
        admin1 = str(location.get("admin1", "")).casefold()
        admin2 = str(location.get("admin2", "")).casefold()
        name = str(location.get("name", "")).casefold()
        return (4 if state_key in admin1 or admin1 in state_key else 0) + (
            3 if district_key in admin2 or admin2 in district_key else 0
        ) + (1 if city.casefold() in name else 0)

    return max(results, key=score)


def get_weather(location: dict[str, Any]) -> dict[str, Any]:
    """Fetch current conditions and a short daily outlook for a geocoded place."""
    try:
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise WeatherLookupError("Weather data could not be loaded right now. Please try again.") from exc


def describe_weather(code: int | None) -> tuple[str, str]:
    """Return a readable label and emoji for a WMO weather code."""
    if code is None:
        return "Conditions unavailable", "🌡️"
    if code == 0:
        return "Clear sky", "☀️"
    if code in (1, 2, 3):
        return "Mainly clear" if code == 1 else ("Partly cloudy" if code == 2 else "Overcast"), "⛅"
    if code in (45, 48):
        return "Foggy", "🌫️"
    if code in (51, 53, 55, 56, 57):
        return "Drizzle", "🌦️"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "Rain", "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "Snow", "❄️"
    if code in (95, 96, 99):
        return "Thunderstorm", "⛈️"
    return "Changeable conditions", "🌤️"


def build_weather_view(location: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    current = data.get("current", {})
    daily = data.get("daily", {})
    label, icon = describe_weather(current.get("weather_code"))
    days = []
    for index, date in enumerate(daily.get("time", [])):
        day_label, day_icon = describe_weather(daily.get("weather_code", [])[index])
        days.append({
            "date": date,
            "label": day_label,
            "icon": day_icon,
            "high": daily.get("temperature_2m_max", [None] * 5)[index],
            "low": daily.get("temperature_2m_min", [None] * 5)[index],
            "rain": daily.get("precipitation_probability_max", [None] * 5)[index],
        })
    return {
        "place": location.get("name", "Selected location"),
        "district": location.get("admin2") or location.get("admin1") or "",
        "state": location.get("admin1", ""),
        "country": location.get("country", "India"),
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "wind": current.get("wind_speed_10m"),
        "precipitation": current.get("precipitation"),
        "label": label,
        "icon": icon,
        "days": days,
        "units": data.get("current_units", {}),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    form = {key: request.form.get(key, "").strip() for key in ("country", "state", "city", "district")}

    if request.method == "POST":
        if not all(form.values()):
            flash("Please fill in the state, city, and district fields.", "error")
        else:
            try:
                location = find_location(form["city"], form["district"], form["state"], form["country"])
                weather = build_weather_view(location, get_weather(location))
            except WeatherLookupError as exc:
                flash(str(exc), "error")

    return render_template("index.html", weather=weather, form=form)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")


