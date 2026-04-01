import json
from unittest.mock import MagicMock

import pytest
from httpx import Response

from intervals_icu_mcp.tools.activity_analysis import (
    get_activity_intervals,
)


@pytest.fixture
def mock_intervals_list():
    """Sample intervals data as a list (direct API response)."""
    return [
        {
            "id": "i129223654",
            "type": "WORK",
            "start": 300,
            "end": 600,
            "duration": 300,
            "average_watts": 250,
            "normalized_power": 255,
            "average_heartrate": 155,
            "max_heartrate": 165,
            "average_cadence": 95,
            "average_speed": 8.5,
            "distance": 2550,
            "target": "250w",
            "target_min": 245,
            "target_max": 255,
        },
        {
            "id": "i129223655",
            "type": "REST",
            "start": 600,
            "end": 720,
            "duration": 120,
            "average_watts": 100,
            "average_heartrate": 120,
        },
    ]


@pytest.fixture
def mock_intervals_dto():
    """Sample intervals data as IntervalsDTO wrapper."""
    return {
        "id": "129223654",
        "analyzed": "2025-10-13T10:00:00",
        "icu_intervals": [
            {
                "id": "i129223654",
                "type": "WORK",
                "start": 300,
                "end": 600,
                "duration": 300,
                "average_watts": 250,
                "normalized_power": 255,
                "average_heartrate": 155,
                "max_heartrate": 165,
                "average_cadence": 95,
                "average_speed": 8.5,
                "distance": 2550,
                "target": "250w",
                "target_min": 245,
                "target_max": 255,
            },
            {
                "id": "i129223655",
                "type": "REST",
                "start": 600,
                "end": 720,
                "duration": 120,
                "average_watts": 100,
                "average_heartrate": 120,
            },
        ],
        "icu_groups": [],
    }


class TestGetActivityIntervals:
    """Tests for get_activity_intervals tool."""

    async def test_get_activity_intervals_list_format(
        self,
        mock_config,
        respx_mock,
        mock_intervals_list,
    ):
        """Test intervals returned as direct list (activity object format)."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        activity_id = "129223654"
        respx_mock.get(f"/activity/{activity_id}/intervals").mock(
            return_value=Response(200, json=mock_intervals_list)
        )

        result = await get_activity_intervals(activity_id=activity_id, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "intervals" in response["data"]
        assert len(response["data"]["intervals"]) == 2
        assert response["data"]["intervals"][0]["id"] == "i129223654"
        assert response["data"]["intervals"][0]["type"] == "WORK"
        assert response["data"]["intervals"][1]["type"] == "REST"
        assert response["data"]["summary"]["total_intervals"] == 2
        assert response["data"]["summary"]["work_intervals"] == 1
        assert response["data"]["summary"]["rest_intervals"] == 1

    async def test_get_activity_intervals_dto_format(
        self,
        mock_config,
        respx_mock,
        mock_intervals_dto,
    ):
        """Test intervals returned as IntervalsDTO wrapper."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        activity_id = "129223654"
        respx_mock.get(f"/activity/{activity_id}/intervals").mock(
            return_value=Response(200, json=mock_intervals_dto)
        )

        result = await get_activity_intervals(activity_id=activity_id, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert "intervals" in response["data"]
        assert len(response["data"]["intervals"]) == 2
        assert response["data"]["intervals"][0]["id"] == "i129223654"

    async def test_get_activity_intervals_empty(
        self,
        mock_config,
        respx_mock,
    ):
        """Test empty intervals response."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        activity_id = "129223654"
        respx_mock.get(f"/activity/{activity_id}/intervals").mock(
            return_value=Response(200, json=[])
        )

        result = await get_activity_intervals(activity_id=activity_id, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["intervals"] == []
        assert response["data"]["count"] == 0

    async def test_get_activity_intervals_string_id(
        self,
        mock_config,
        respx_mock,
        mock_intervals_list,
    ):
        """Test that string interval IDs are properly handled."""
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        activity_id = "i129223654"
        respx_mock.get(f"/activity/{activity_id}/intervals").mock(
            return_value=Response(200, json=mock_intervals_list)
        )

        result = await get_activity_intervals(activity_id=activity_id, ctx=mock_ctx)

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["intervals"][0]["id"] == "i129223654"
