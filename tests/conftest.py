"""Pytest configuration and shared fixtures."""

import pytest
import respx

from intervals_icu_mcp.auth import ICUConfig


@pytest.fixture
def mock_config():
    """Provide a mock ICU configuration for testing."""
    return ICUConfig(
        intervals_icu_api_key="test_api_key_12345",
        intervals_icu_athlete_id="i123456",
    )


@pytest.fixture
def respx_mock():
    """Provide a respx mock router for HTTP requests."""
    with respx.mock(
        base_url="https://intervals.icu/api/v1",
        assert_all_called=False,
    ) as respx_mock:
        yield respx_mock


@pytest.fixture
def mock_athlete_data():
    """Sample athlete data for testing."""
    return {
        "id": "i123456",
        "name": "Test Athlete",
        "email": "test@example.com",
        "weight": 70.0,
        "ctl": 50.0,
        "atl": 35.0,
        "tsb": 15.0,
        "ramp_rate": 3.5,
        "sport_settings": [
            {
                "id": 1,
                "type": "Ride",
                "ftp": 250,
                "fthr": 165,
            }
        ],
    }


@pytest.fixture
def mock_activity_data():
    """Sample activity data for testing."""
    return {
        "id": "12345",
        "start_date_local": "2025-10-13T08:00:00",
        "name": "Morning Ride",
        "type": "Ride",
        "distance": 50000.0,  # meters
        "moving_time": 7200,  # seconds
        "elapsed_time": 7500,
        "total_elevation_gain": 500.0,
        "average_speed": 6.94,  # m/s
        "average_watts": 200,
        "normalized_power": 210,
        "average_heartrate": 145,
        "icu_training_load": 120,
        "icu_intensity": 0.84,
        "has_weather": True,
        "average_weather_temp": 18.5,
        "min_weather_temp": 12.0,
        "max_weather_temp": 24.0,
        "average_feels_like": 17.0,
        "min_feels_like": 10.0,
        "max_feels_like": 22.0,
        "average_wind_speed": 15.0,
        "average_wind_gust": 25.0,
        "prevailing_wind_deg": 180,
        "headwind_percent": 30.0,
        "tailwind_percent": 70.0,
        "average_clouds": 50,
        "max_rain": 0.0,
        "max_snow": 0.0,
    }


@pytest.fixture
def mock_activity_data_no_weather():
    """Sample activity data without weather fields."""
    return {
        "id": "12345",
        "start_date_local": "2025-10-13T08:00:00",
        "name": "Morning Ride",
        "type": "Ride",
        "distance": 50000.0,
        "moving_time": 7200,
        "elapsed_time": 7500,
        "total_elevation_gain": 500.0,
        "average_speed": 6.94,
        "average_watts": 200,
        "normalized_power": 210,
        "average_heartrate": 145,
        "icu_training_load": 120,
        "icu_intensity": 0.84,
    }


@pytest.fixture
def mock_wellness_data():
    """Sample wellness data for testing."""
    return {
        "id": "2025-10-13",
        "weight": 70.0,
        "restingHR": 48,
        "hrv": 65.5,
        "hrvSDNN": 75.2,
        "sleepSecs": 28800,  # 8 hours
        "sleepQuality": 8,
        "sleepScore": 85.0,
        "fatigue": 3,
        "soreness": 2,
        "stress": 2,
        "mood": 8,
        "motivation": 9,
        "ctl": 50.0,
        "atl": 35.0,
        "tsb": 15.0,
    }


@pytest.fixture
def mock_event_data():
    """Sample event data for testing."""
    return {
        "id": 1001,
        "start_date_local": "2025-10-14",
        "category": "WORKOUT",
        "name": "Threshold Intervals",
        "type": "Ride",
        "description": "5x5min @ FTP",
        "moving_time": 3600,
        "icu_training_load": 100,
        "icu_intensity": 0.90,
    }


@pytest.fixture
def mock_power_curve_data():
    """Sample power curve data for testing."""
    return {
        "name": "Power Curve",
        "type": "power",
        "athlete_id": "i123456",
        "data": [
            {"secs": 5, "watts": 800, "date": "2025-10-01"},
            {"secs": 60, "watts": 400, "date": "2025-10-05"},
            {"secs": 300, "watts": 300, "date": "2025-10-08"},
            {"secs": 1200, "watts": 250, "date": "2025-10-12"},
        ],
    }
