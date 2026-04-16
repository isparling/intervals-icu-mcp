"""Tests for wellness tools."""

import json
from unittest.mock import MagicMock

from httpx import Response

from intervals_icu_mcp.tools.wellness import get_wellness_data


class TestGetWellnessData:
    """Tests for get_wellness_data tool."""

    async def test_get_wellness_data_with_days_back_int(
        self,
        mock_config,
        respx_mock,
        mock_wellness_data,
    ):
        """Test with integer days_back parameter."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/wellness").mock(
            return_value=Response(200, json=[mock_wellness_data])
        )

        result = await get_wellness_data(days_back=7, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "wellness_data" in response["data"]

    async def test_get_wellness_data_with_days_back_string(
        self,
        mock_config,
        respx_mock,
        mock_wellness_data,
    ):
        """Test with string days_back parameter (should be coerced to int)."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/wellness").mock(
            return_value=Response(200, json=[mock_wellness_data])
        )

        result = await get_wellness_data(days_back="7", ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "wellness_data" in response["data"]

    async def test_get_wellness_data_with_date_range(
        self,
        mock_config,
        respx_mock,
        mock_wellness_data,
    ):
        """Test with start_date and end_date parameters."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/wellness").mock(
            return_value=Response(200, json=[mock_wellness_data])
        )

        result = await get_wellness_data(
            start_date="2026-04-05",
            end_date="2026-04-16",
            ctx=mock_ctx,
        )

        response = json.loads(result)
        assert "data" in response
        assert "wellness_data" in response["data"]

    async def test_get_wellness_data_empty_response(
        self,
        mock_config,
        respx_mock,
    ):
        """Test handling of empty wellness data."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        respx_mock.get("/athlete/i123456/wellness").mock(return_value=Response(200, json=[]))

        result = await get_wellness_data(ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["wellness_data"] == []
        assert response["data"]["count"] == 0
