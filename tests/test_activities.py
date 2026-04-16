"""Tests for activity tools."""

import json
from unittest.mock import MagicMock

from httpx import Response

from intervals_icu_mcp.tools.activities import get_recent_activities


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
