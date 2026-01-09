# Weather Command

Get current weather and forecasts for any location worldwide.

## How to Use

Invoke with: `/weather <location>` (e.g., `/weather San Diego`)

**Arguments provided:** $ARGUMENTS

When the user invokes `/weather`, help them get weather information using the Weather MCP tool.

### Available Functions

1. **Current Weather** - Get current conditions for a location
2. **With Forecast** - Get current conditions plus a 3-day forecast

### Example Locations
- City names: `San Diego`, `Los Angeles`, `New York`
- City with state: `La Jolla, CA`, `Austin, TX`
- Zip codes: `92093` (UCSD), `90210`
- International: `London`, `Tokyo`, `Paris`

## Instructions for Claude

When the user runs this command:

1. **Check $ARGUMENTS** - If a location was provided (e.g., `/weather San Diego`), use it directly.
   If $ARGUMENTS is empty, ask: "What location would you like weather for?"

2. **Use the Weather MCP tool** to fetch the weather:
   - Tool: `mcp__weather-mcp__weather_tool`
   - Parameters:
     - `location`: The location to get weather for
     - `include_forecast`: Set to `true` if user wants a forecast

3. **Present the results** in a clear, friendly format

4. **Offer follow-up options**:
   - "Would you like a 3-day forecast?"
   - "Want to check another location?"

## Demo Notes

This is a demonstration command for the UCSD AI Use Case presentation. It shows:
- How Claude Code slash commands work (`/weather`)
- Integration between Claude and MCP tools
- Real-time API data fetching (using wttr.in - no API key needed)

The weather data comes from wttr.in, a free weather service.
