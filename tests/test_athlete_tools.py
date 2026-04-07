"""Tests for athlete tools."""

import json
from datetime import date
from unittest.mock import MagicMock

from httpx import Response

from intervals_icu_mcp.tools.athlete import get_athlete_profile, get_fitness_summary


class TestGetAthleteProfile:
    """Tests for get_athlete_profile tool."""

    async def test_get_athlete_profile_success(
        self,
        mock_config,
        respx_mock,
        mock_athlete_data,
        mock_wellness_data,
    ):
        """Test successful athlete profile retrieval."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        today = date.today().isoformat()
        respx_mock.get("/athlete/i123456").mock(return_value=Response(200, json=mock_athlete_data))
        respx_mock.get(f"/athlete/i123456/wellness/{today}").mock(
            return_value=Response(200, json=mock_wellness_data)
        )

        result = await get_athlete_profile(ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "profile" in response["data"]
        assert response["data"]["profile"]["name"] == "Test Athlete"
        assert response["data"]["profile"]["id"] == "i123456"
        assert response["data"]["profile"]["email"] == "test@example.com"
        assert response["data"]["profile"]["weight_kg"] == 70.0


class TestGetFitnessSummary:
    """Tests for get_fitness_summary tool."""

    async def test_get_fitness_summary_success(
        self,
        mock_config,
        respx_mock,
        mock_athlete_data,
        mock_wellness_data,
    ):
        """Test successful fitness summary retrieval."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        today = date.today().isoformat()
        respx_mock.get("/athlete/i123456").mock(return_value=Response(200, json=mock_athlete_data))
        respx_mock.get(f"/athlete/i123456/wellness/{today}").mock(
            return_value=Response(200, json=mock_wellness_data)
        )

        result = await get_fitness_summary(ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "fitness_metrics" in response["data"]
        assert "ctl" in response["data"]["fitness_metrics"]

    async def test_get_fitness_summary_with_high_ramp_rate(
        self,
        mock_config,
        respx_mock,
        mock_athlete_data,
        mock_wellness_data,
    ):
        """Test fitness summary with high ramp rate warning."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        wellness_data = mock_wellness_data.copy()
        wellness_data["rampRate"] = 10.0

        today = date.today().isoformat()
        respx_mock.get("/athlete/i123456").mock(return_value=Response(200, json=mock_athlete_data))
        respx_mock.get(f"/athlete/i123456/wellness/{today}").mock(
            return_value=Response(200, json=wellness_data)
        )

        result = await get_fitness_summary(ctx=mock_ctx)

        response = json.loads(result)
        assert "analysis" in response
        assert "ramp_rate_status" in response["analysis"]
        assert response["analysis"]["ramp_rate_status"] == "high_risk"
