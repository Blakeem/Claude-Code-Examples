---
name: weather-skill
description: Get current weather and forecasts for any location worldwide.
allowed-tools:
  - Bash
  - Read
---

# Weather Skill

This skill provides weather information using the `.claude/skills/weather-skill/weather/weather.py` utility.

## Slash Command Usage

Users can invoke this skill with: `/weather-skill <location>`

Example: `/weather-skill San Diego`

**Arguments provided by user:** $ARGUMENTS

If the user provided a location argument, use it directly. If no argument was provided, ask what location they'd like weather for.

## Quick Start

Run the weather script with a location:

```bash
python .claude/skills/weather-skill/weather/weather.py "San Diego"
```

For a 3-day forecast:

```bash
python .claude/skills/weather-skill/weather/weather.py "San Diego" --forecast
```

## Supported Location Formats

| Format | Example |
|--------|---------|
| City name | `San Diego`, `London`, `Tokyo` |
| City, State | `La Jolla, CA`, `Austin, TX` |
| Zip code | `92093`, `90210` |
| Country | `France`, `Japan` |

## Response Guidelines

When providing weather information:

1. Present temperature in both Fahrenheit and Celsius
2. Include key details: conditions, humidity, wind
3. Offer to show the forecast if showing current weather
4. Be conversational and helpful

## Technical Details

- Data source: wttr.in (free, no API key required)
- Script location: `.claude/skills/weather-skill/weather/weather.py`
- Requires: Python 3.x with standard library only
