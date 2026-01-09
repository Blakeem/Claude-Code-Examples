#!/usr/bin/env python3
"""
Weather MCP Server - Demo for UCSD AI Use Case Presentation

This MCP server demonstrates all three MCP primitives:
- Tools: Functions that Claude can call (weather_tool)
- Prompts: Templates that appear as slash commands (/weather)
- Resources: Data that can be read (supported locations info)

Install: pip install "mcp[cli]"
Test: npx @modelcontextprotocol/inspector python mcp-server/weather_server.py
Configure: claude mcp add weather-mcp -- python mcp-server/weather_server.py
"""

import sys
import os

# Add skills/weather-skill directory to path so we can import the weather module
plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(plugin_root, "skills", "weather-skill"))

from mcp.server.fastmcp import FastMCP
from weather import get_weather, format_weather_report, get_forecast

# Create the MCP server
mcp = FastMCP("Weather MCP")


# ============ TOOL ============
# This tool can be called by Claude to fetch weather data

@mcp.tool()
def weather_tool(location: str, include_forecast: bool = False) -> dict:
    """
    Get current weather and optionally a 3-day forecast for any location.

    Args:
        location: City name, zip code, or location (e.g., "San Diego", "92093", "Tokyo")
        include_forecast: If True, include a 3-day forecast

    Returns:
        Weather data as JSON with current conditions and optional forecast
    """
    data = get_weather(location)

    # Handle errors
    if "error" in data:
        return {"error": data["error"]}

    try:
        current = data["current_condition"][0]
        location_info = data["nearest_area"][0]

        result = {
            "location": {
                "city": location_info["areaName"][0]["value"],
                "region": location_info["region"][0]["value"],
                "country": location_info["country"][0]["value"]
            },
            "current": {
                "condition": current["weatherDesc"][0]["value"],
                "temp_f": int(current["temp_F"]),
                "temp_c": int(current["temp_C"]),
                "feels_like_f": int(current["FeelsLikeF"]),
                "feels_like_c": int(current["FeelsLikeC"]),
                "humidity": int(current["humidity"]),
                "wind_mph": int(current["windspeedMiles"]),
                "wind_direction": current["winddir16Point"],
                "uv_index": int(current["uvIndex"]),
                "visibility_miles": int(current["visibility"])
            }
        }

        if include_forecast:
            forecasts = data.get("weather", [])[:3]
            result["forecast"] = [
                {
                    "date": day["date"],
                    "high_f": int(day["maxtempF"]),
                    "low_f": int(day["mintempF"]),
                    "condition": day["hourly"][4]["weatherDesc"][0]["value"]
                }
                for day in forecasts
            ]

        return result

    except (KeyError, IndexError) as e:
        return {"error": f"Failed to parse weather data: {e}"}


# ============ PROMPT ============
# This prompt appears as a slash command in Claude Code
# Note: MCP prompts split arguments by spaces - multi-word values not yet supported

@mcp.prompt()
def weather(location: str = "") -> str:
    """
    Get current weather and forecasts for any location worldwide.

    Args:
        location: Zip code or single-word city (e.g., 92041, Tokyo, London)
    """
    if location:
        return f"""The user wants weather information for: {location}

Please use the weather_tool to fetch the current weather for this location.
Present the results in a friendly, conversational format.
Offer to show the 3-day forecast if they're interested."""
    else:
        return """The user wants weather information but didn't specify a location.

Please ask them: "What location would you like weather for? You can give me a city name, zip code, or any location worldwide."

Once they provide a location, use the weather_tool to fetch the weather."""


# ============ RESOURCE ============
# Resources expose data that can be read by the LLM

@mcp.resource("weather://help")
def weather_help() -> str:
    """Information about how to use the weather service."""
    return """# Weather Service Help

## Supported Location Formats
- **City name**: Tokyo, London, Paris
- **City, State**: San Diego, CA (note: use underscores for MCP prompts)
- **Zip code**: 92093, 91941, 90210
- **Country**: France, Japan, Australia

## Available Features
- Current conditions (temperature, humidity, wind)
- 3-day forecast

## Data Source
Weather data provided by wttr.in (free, no API key required).
"""


# ============ RUN SERVER ============
if __name__ == "__main__":
    mcp.run()
