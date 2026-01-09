#!/usr/bin/env python3
"""
Weather Utility - Fetches weather data with fallback providers

This is a demo script for the UCSD AI Use Case presentation showing
how Claude Code skills and slash commands work.

Primary: wttr.in (no API key required)
Fallback: Open-Meteo (no API key required, more reliable)

Usage:
    python weather.py <location>
    python weather.py "San Diego"
    python weather.py "La Jolla, CA"
    python weather.py 92093  # UCSD zip code
"""

import sys
import urllib.request
import urllib.parse
import json

# WMO Weather interpretation codes (https://open-meteo.com/en/docs)
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
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


def _geocode_location(location: str) -> tuple:
    """
    Convert a location name to coordinates using Open-Meteo Geocoding API.

    Args:
        location: City name, zip code, or place name

    Returns:
        Tuple of (latitude, longitude, city_name, region, country) or None on failure
    """
    encoded = urllib.parse.quote(location)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=en&format=json"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return (
                    result["latitude"],
                    result["longitude"],
                    result.get("name", location),
                    result.get("admin1", ""),  # region/state
                    result.get("country", "")
                )
    except Exception:
        pass
    return None


def _get_weather_open_meteo(location: str) -> dict:
    """
    Fetch weather data from Open-Meteo API (fallback provider).

    Args:
        location: City name, zip code, or place name

    Returns:
        Weather data in wttr.in-compatible format, or dict with "error" key
    """
    # First geocode the location
    geo = _geocode_location(location)
    if geo is None:
        return {"error": f"Could not find location: {location}"}

    lat, lon, city, region, country = geo

    # Fetch weather data
    current_vars = "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    daily_vars = "weather_code,temperature_2m_max,temperature_2m_min"
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current={current_vars}"
        f"&daily={daily_vars}"
        f"&temperature_unit=fahrenheit"
        f"&wind_speed_unit=mph"
        f"&timezone=auto"
        f"&forecast_days=3"
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": f"Open-Meteo API failed: {e}"}

    # Convert to wttr.in-compatible format
    try:
        current = data["current"]
        daily = data.get("daily", {})

        # Map wind direction degrees to 16-point compass
        wind_deg = current.get("wind_direction_10m", 0)
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        wind_dir = directions[int((wind_deg + 11.25) / 22.5) % 16]

        weather_code = current.get("weather_code", 0)
        weather_desc = WMO_CODES.get(weather_code, "Unknown")

        # Convert Fahrenheit to Celsius for compatibility
        temp_f = current.get("temperature_2m", 70)
        temp_c = round((temp_f - 32) * 5 / 9)
        feels_f = current.get("apparent_temperature", temp_f)
        feels_c = round((feels_f - 32) * 5 / 9)

        result = {
            "current_condition": [{
                "temp_F": str(round(temp_f)),
                "temp_C": str(temp_c),
                "FeelsLikeF": str(round(feels_f)),
                "FeelsLikeC": str(feels_c),
                "humidity": str(current.get("relative_humidity_2m", 50)),
                "weatherDesc": [{"value": weather_desc}],
                "windspeedMiles": str(round(current.get("wind_speed_10m", 0))),
                "winddir16Point": wind_dir,
                "uvIndex": "0",  # Not available in current Open-Meteo free tier
                "visibility": "10",  # Not available, default to good visibility
            }],
            "nearest_area": [{
                "areaName": [{"value": city}],
                "region": [{"value": region}],
                "country": [{"value": country}],
            }],
            "weather": [],
            "_provider": "open-meteo"  # Mark which provider was used
        }

        # Add forecast data
        if "time" in daily:
            for i, date in enumerate(daily["time"][:3]):
                max_f = daily.get("temperature_2m_max", [70, 70, 70])[i]
                min_f = daily.get("temperature_2m_min", [50, 50, 50])[i]
                code = daily.get("weather_code", [0, 0, 0])[i]

                result["weather"].append({
                    "date": date,
                    "maxtempF": str(round(max_f)),
                    "mintempF": str(round(min_f)),
                    "hourly": [
                        {"weatherDesc": [{"value": ""}]},
                        {"weatherDesc": [{"value": ""}]},
                        {"weatherDesc": [{"value": ""}]},
                        {"weatherDesc": [{"value": ""}]},
                        {"weatherDesc": [{"value": WMO_CODES.get(code, "Unknown")}]},
                    ]
                })

        return result

    except (KeyError, IndexError, TypeError) as e:
        return {"error": f"Failed to parse Open-Meteo data: {e}"}


def _get_weather_wttr(location: str) -> dict:
    """
    Fetch weather data from wttr.in (primary provider).

    Args:
        location: City name, zip code, or coordinates

    Returns:
        Weather data dictionary or dict with "error" key
    """
    encoded_location = urllib.parse.quote(location)
    url = f"https://wttr.in/{encoded_location}?format=j1"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            result = json.loads(data)
            result["_provider"] = "wttr.in"
            return result
    except urllib.error.URLError as e:
        return {"error": f"wttr.in failed: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"wttr.in parse error: {e}"}


def get_weather(location: str, format_type: str = "json") -> dict:
    """
    Fetch weather data for a given location with automatic fallback.

    Primary: wttr.in
    Fallback: Open-Meteo (if wttr.in fails)

    Args:
        location: City name, zip code, or coordinates
        format_type: "json" for data, "text" for formatted output

    Returns:
        Weather data dictionary or formatted string
    """
    if format_type == "text":
        # Text format only supported by wttr.in
        encoded_location = urllib.parse.quote(location)
        url = f"https://wttr.in/{encoded_location}?format=%l:+%c+%t+(%f)+%h+humidity,+%w+wind"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return f"Error: {e}"

    # JSON format: try wttr.in first, fall back to Open-Meteo
    result = _get_weather_wttr(location)

    if "error" in result:
        # wttr.in failed, try Open-Meteo fallback
        fallback_result = _get_weather_open_meteo(location)
        if "error" not in fallback_result:
            return fallback_result
        # Both failed, return original error with note about fallback
        return {"error": f"{result['error']} | Fallback also failed: {fallback_result['error']}"}

    return result


def format_weather_report(data: dict) -> str:
    """
    Format weather data into a readable report.

    Args:
        data: Weather data dictionary from wttr.in

    Returns:
        Formatted weather report string
    """
    if "error" in data:
        return f"Error: {data['error']}"

    try:
        current = data["current_condition"][0]
        location_info = data["nearest_area"][0]

        # Extract location details
        city = location_info["areaName"][0]["value"]
        region = location_info["region"][0]["value"]
        country = location_info["country"][0]["value"]

        # Extract weather details
        temp_f = current["temp_F"]
        temp_c = current["temp_C"]
        feels_like_f = current["FeelsLikeF"]
        feels_like_c = current["FeelsLikeC"]
        humidity = current["humidity"]
        description = current["weatherDesc"][0]["value"]
        wind_mph = current["windspeedMiles"]
        wind_dir = current["winddir16Point"]
        uv_index = current["uvIndex"]
        visibility = current["visibility"]

        report = f"""
+--------------------------------------------------------------+
|                    WEATHER REPORT                            |
+--------------------------------------------------------------+
|  Location: {city}, {region}, {country}
|
|  Current Conditions: {description}
|
|  Temperature: {temp_f}F ({temp_c}C)
|  Feels Like:  {feels_like_f}F ({feels_like_c}C)
|
|  Humidity:    {humidity}%
|  Wind:        {wind_mph} mph {wind_dir}
|  UV Index:    {uv_index}
|  Visibility:  {visibility} miles
+--------------------------------------------------------------+
"""
        return report

    except (KeyError, IndexError) as e:
        return f"Error parsing weather data: {e}"


def get_forecast(location: str, days: int = 3) -> str:
    """
    Get a multi-day forecast for a location.

    Args:
        location: City name, zip code, or coordinates
        days: Number of days (1-3)

    Returns:
        Formatted forecast string
    """
    data = get_weather(location)

    if "error" in data:
        return f"Error: {data['error']}"

    try:
        forecasts = data.get("weather", [])[:days]
        location_info = data["nearest_area"][0]
        city = location_info["areaName"][0]["value"]

        lines = [f"\n{days}-Day Forecast for {city}:\n" + "=" * 50]

        for day in forecasts:
            date = day["date"]
            max_temp = day["maxtempF"]
            min_temp = day["mintempF"]
            desc = day["hourly"][4]["weatherDesc"][0]["value"]  # Midday weather

            lines.append(f"\n{date}")
            lines.append(f"  High: {max_temp}F  |  Low: {min_temp}F")
            lines.append(f"  Conditions: {desc}")

        return "\n".join(lines)

    except (KeyError, IndexError) as e:
        return f"Error parsing forecast data: {e}"


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample locations:")
        print("  - San Diego")
        print("  - La Jolla, CA")
        print("  - 92093 (UCSD)")
        print("  - London")
        print("  - Tokyo")
        sys.exit(1)

    location = " ".join(sys.argv[1:])

    # Check for forecast flag
    if "--forecast" in location:
        location = location.replace("--forecast", "").strip()
        print(get_forecast(location))
    else:
        data = get_weather(location)
        print(format_weather_report(data))


if __name__ == "__main__":
    main()
