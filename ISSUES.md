# intervals-icu-mcp — Local Issue Backlog

Informal local tracking for pick-up-later work. Not GitHub issues (yet).

---

## Open

### 3. Dedicated weather summary tool
**Priority:** low · **Source:** follow-up from issue #1

The `GET /activity/{id}/weather-summary` endpoint returns richer weather data than the Activity-level fields: directional wind rose breakdowns, apparent wind, weather descriptions, and supports sub-activity time ranges via `start_index`/`end_index` params.

- Add `get_activity_weather_summary` client method and tool.
- Expose wind rose, apparent wind, and weather description fields.

---

## Done

### 1. Surface weather + temperature on activities ✓
**Priority:** medium · **Source:** claw-coach race-analysis (24 Hours in the Enchanted Forest)

Added 17 weather fields to the `Activity` model and a structured `"weather"` section to `get_activity_details` output (temperature, wind, conditions). See `models.py`, `tools/activities.py`.

### 2. Expose Normalized Power + moving time in get_activity_details ✓
**Priority:** low · **Source:** claw-coach race-analysis (24 Hours in the Enchanted Forest)

Already implemented: `normalized_power` in `power.normalized`, `moving_time` in `moving_time_seconds`, `elapsed_time` in `elapsed_time_seconds`. All fields modeled in `ActivitySummary` and exposed in tool output.
