"""Tests for activity tools."""

import json
from unittest.mock import MagicMock

from httpx import Response

from intervals_icu_mcp.tools.activities import get_activity_details, get_recent_activities


class TestGetRecentActivities:
    """Tests for get_recent_activities tool."""

    async def test_get_recent_activities_with_int_limit(
        self,
        mock_config,
        respx_mock,
        mock_activity_data,
    ):
        """Test with integer limit parameter."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/activities").mock(
            return_value=Response(200, json=[mock_activity_data])
        )

        result = await get_recent_activities(limit=5, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "activities" in response["data"]

    async def test_get_recent_activities_with_string_limit(
        self,
        mock_config,
        respx_mock,
        mock_activity_data,
    ):
        """Test with string limit parameter (should be coerced to int)."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/activities").mock(
            return_value=Response(200, json=[mock_activity_data])
        )

        result = await get_recent_activities(limit="5", ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "activities" in response["data"]

    async def test_get_recent_activities_with_string_days_back(
        self,
        mock_config,
        respx_mock,
        mock_activity_data,
    ):
        """Test with string days_back parameter (should be coerced to int)."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/activities").mock(
            return_value=Response(200, json=[mock_activity_data])
        )

        result = await get_recent_activities(days_back="14", ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "activities" in response["data"]

    async def test_get_recent_activities_empty_response(
        self,
        mock_config,
        respx_mock,
    ):
        """Test handling of empty activity list."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/activities").mock(return_value=Response(200, json=[]))

        result = await get_recent_activities(ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["activities"] == []
        assert response["data"]["count"] == 0


class TestGetActivityDetailsWeather:
    """Tests for weather section in get_activity_details."""

    async def test_weather_fields_present(
        self,
        mock_config,
        respx_mock,
        mock_activity_data,
    ):
        """Test that weather section is included when weather data exists."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/activity/12345").mock(
            return_value=Response(200, json=mock_activity_data)
        )

        result = await get_activity_details(activity_id="12345", ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        weather = response["data"]["weather"]
        assert weather["available"] is True
        assert weather["temperature"]["average_weather_temp"] == 18.5
        assert weather["temperature"]["min_weather_temp"] == 12.0
        assert weather["temperature"]["max_weather_temp"] == 24.0
        assert weather["temperature"]["average_feels_like"] == 17.0
        assert weather["wind"]["average_speed_kmh"] == 15.0
        assert weather["wind"]["prevailing_direction_deg"] == 180
        assert weather["conditions"]["average_clouds_percent"] == 50

    async def test_weather_fields_absent(
        self,
        mock_config,
        respx_mock,
        mock_activity_data_no_weather,
    ):
        """Test that weather section is omitted when no weather data exists."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/activity/12345").mock(
            return_value=Response(200, json=mock_activity_data_no_weather)
        )

        result = await get_activity_details(activity_id="12345", ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "weather" not in response["data"]

    async def test_weather_partial_data(
        self,
        mock_config,
        respx_mock,
    ):
        """Test weather section with only temperature data (no wind/conditions)."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        activity_data = {
            "id": "12345",
            "start_date_local": "2025-10-13T08:00:00",
            "name": "Morning Ride",
            "type": "Ride",
            "has_weather": True,
            "average_weather_temp": 20.0,
            "min_weather_temp": 15.0,
            "max_weather_temp": 25.0,
        }

        respx_mock.get("/activity/12345").mock(
            return_value=Response(200, json=activity_data)
        )

        result = await get_activity_details(activity_id="12345", ctx=mock_ctx)

        response = json.loads(result)
        weather = response["data"]["weather"]
        assert weather["available"] is True
        assert "temperature" in weather
        assert "wind" not in weather
        assert "conditions" not in weather
