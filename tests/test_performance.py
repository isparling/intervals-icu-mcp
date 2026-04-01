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
        "data": [
            {"secs": 5, "watts": 800, "date": "2025-10-01", "src_activity_id": "a1"},
            {"secs": 15, "watts": 650, "date": "2025-10-03", "src_activity_id": "a2"},
            {"secs": 60, "watts": 400, "date": "2025-10-05", "src_activity_id": "a3"},
            {"secs": 300, "watts": 300, "date": "2025-10-08", "src_activity_id": "a4"},
            {"secs": 1200, "watts": 250, "date": "2025-10-12", "src_activity_id": "a5"},
            {"secs": 3600, "watts": 200, "date": "2025-10-15", "src_activity_id": "a6"},
        ],
    }


@pytest.fixture
def mock_empty_power_curve_data():
    return {
        "name": "Power Curve",
        "type": "power",
        "athlete_id": "i123456",
        "data": [],
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

    async def test_get_power_curves_includes_f1_parameter(
        self,
        mock_config,
        respx_mock,
        mock_power_curve_data,
    ):
        """Test that f1 filter parameter is included in request."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        route = respx_mock.get("/athlete/i123456/power-curves.json").mock(
            return_value=Response(200, json=mock_power_curve_data)
        )

        await get_power_curves(ctx=mock_ctx, activity_type="VirtualRide")

        assert route.call_count == 1
        request = route.calls[0].request
        assert "f1=" in str(request.url)

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
