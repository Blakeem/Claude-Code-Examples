#!/usr/bin/env python3
"""
Weather Utility - Fetches weather data from wttr.in (no API key required)

This is a demo script for the UCSD AI Use Case presentation showing
how Claude Code skills and slash commands work.

Usage:
    python weather.py <location>
    python weather.py "San Diego"
    python weather.py "La Jolla, CA"
    python weather.py 92093  # UCSD zip code
"""

import sys
import urllib.request
import json


def get_weather(location: str, format_type: str = "json") -> dict:
    """
    Fetch weather data for a given location.

    Args:
        location: City name, zip code, or coordinates
        format_type: "json" for data, "text" for formatted output

    Returns:
        Weather data dictionary or formatted string
    """
    # URL encode the location
    encoded_location = urllib.parse.quote(location)

    if format_type == "json":
        url = f"https://wttr.in/{encoded_location}?format=j1"
    else:
        # Simple one-line format
        url = f"https://wttr.in/{encoded_location}?format=%l:+%c+%t+(%f)+%h+humidity,+%w+wind"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            if format_type == "json":
                return json.loads(data)
            return data
    except urllib.error.URLError as e:
        return {"error": f"Failed to fetch weather: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse weather data: {e}"}


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
    import urllib.parse  # Import here to avoid issues with the function
    main()
