"""Tests for performance curve tools."""

import json
from unittest.mock import MagicMock

import pytest
from httpx import Response

from intervals_icu_mcp.tools.performance import get_power_curves


@pytest.fixture
def mock_power_curve_data():
    return {
        "name": "Power Curve",
        "type": "power",
        "athlete_id": "i123456",
        "list": [
            {
                "id": "90d",
                "label": "90 days",
                "secs": [5, 15, 60, 300, 1200, 3600],
                "values": [800, 650, 400, 300, 250, 200],
                "activity_id": ["a1", "a2", "a3", "a4", "a5", "a6"],
            }
        ],
    }


@pytest.fixture
def mock_empty_power_curve_data():
    return {
        "name": "Power Curve",
        "type": "power",
        "athlete_id": "i123456",
        "list": [],
    }


class TestGetPowerCurves:
    """Tests for get_power_curves tool."""

    async def test_get_power_curves_with_data(
        self,
        mock_config,
        respx_mock,
        mock_power_curve_data,
    ):
        """Test power curve retrieval returns peak efforts."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_power_curve_data)
        )

        result = await get_power_curves(ctx=mock_ctx, activity_type="Ride")

        response = json.loads(result)
        assert "data" in response
        assert "peak_efforts" in response["data"]
        assert "5_sec" in response["data"]["peak_efforts"]
        assert response["data"]["peak_efforts"]["5_sec"]["watts"] == 800
        assert response["data"]["summary"]["total_data_points"] == 6

    async def test_get_power_curves_empty_response(
        self,
        mock_config,
        respx_mock,
        mock_empty_power_curve_data,
    ):
        """Test empty power curve returns helpful message."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_empty_power_curve_data)
        )

        result = await get_power_curves(ctx=mock_ctx, activity_type="Ride")

        response = json.loads(result)
        assert response["data"]["power_curve"] == []
        assert "metadata" in response
        assert "No power curve data" in response["metadata"]["message"]

    async def test_get_power_curves_includes_type_parameter(
        self,
        mock_config,
        respx_mock,
        mock_power_curve_data,
    ):
        """Test that type filter parameter is included in request."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        route = respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_power_curve_data)
        )

        await get_power_curves(ctx=mock_ctx, activity_type="VirtualRide")

        assert route.call_count == 1
        request = route.calls[0].request
        assert "type=VirtualRide" in str(request.url)

    async def test_get_power_curves_with_date_range(
        self,
        mock_config,
        respx_mock,
        mock_power_curve_data,
    ):
        """Test power curve with date range parameters."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        route = respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_power_curve_data)
        )

        result = await get_power_curves(
            ctx=mock_ctx,
            days_back=30,
            activity_type="Ride",
        )

        response = json.loads(result)
        assert route.call_count == 1
        request = route.calls[0].request
        assert "oldest=" in str(request.url)
        assert response["data"]["period"] == "30_days"

    async def test_get_power_curves_time_period_week(
        self,
        mock_config,
        respx_mock,
        mock_power_curve_data,
    ):
        """Test time_period='week' sets correct date range."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_power_curve_data)
        )

        result = await get_power_curves(ctx=mock_ctx, time_period="week")

        response = json.loads(result)
        assert response["data"]["period"] == "week"

    async def test_get_power_curves_invalid_time_period(
        self,
        mock_config,
        respx_mock,
    ):
        """Test invalid time_period returns error."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        result = await get_power_curves(ctx=mock_ctx, time_period="invalid")

        response = json.loads(result)
        assert response["error"] is not None
        assert response["error"]["type"] == "validation_error"
