import pytest
from unittest.mock import patch
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_single_location_weather(mock_geocode, mock_fetch_weather_data, api_client):
    # Mock the weather data response
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-15",
            "weather_code": 2.0,
            "weather_description": "Partly cloudy",
            "temperature_max": 27,
            "temperature_min": 14,
            "uv_index_max": 8,
            "precipitation_probability_max": 0,
            "wind_speed_max": 12,
            "wind_gusts_max": 35,
            "wind_direction": 297,
        },
        {
            "date": "2024-10-16",
            "weather_code": 3.0,
            "weather_description": "Overcast",
            "temperature_max": 21,
            "temperature_min": 15,
            "uv_index_max": 5,
            "precipitation_probability_max": 0,
            "wind_speed_max": 14,
            "wind_gusts_max": 45,
            "wind_direction": 267,
        },
    ]

    # Mock geocoding response
    mock_geocode.return_value = type(
        "Location",
        (object,),
        {
            "latitude": -33.9249,
            "longitude": 18.4241,
            "address": "Cape Town, South Africa",
        },
    )()

    data = [
        {
            "place_name": "Cape Town",
            "start_date": "2024-10-15",
            "end_date": "2024-10-16",
        }
    ]

    response = api_client.post("/api/weather/", data, format="json")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data[0]["place_name"] == "Cape Town"
    assert response_data[0]["weather_data"][0]["weather_description"] == "Partly cloudy"
    assert response_data[0]["weather_data"][1]["wind_direction"] == 267


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_multiple_locations_weather(mock_geocode, mock_fetch_weather_data, api_client):
    # Mock the weather data response for multiple locations
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-14",
            "weather_code": 2.0,
            "weather_description": "Partly cloudy",
            "temperature_max": 20,
            "temperature_min": 12,
            "uv_index_max": 8,
            "precipitation_probability_max": 18,
            "wind_speed_max": 29,
            "wind_gusts_max": 70,
            "wind_direction": 102,
        },
        {
            "date": "2024-10-15",
            "weather_code": 3.0,
            "weather_description": "Overcast",
            "temperature_max": 27,
            "temperature_min": 11,
            "uv_index_max": 8,
            "precipitation_probability_max": 5,
            "wind_speed_max": 10,
            "wind_gusts_max": 26,
            "wind_direction": 101,
        },
    ]

    # Mock geocoding response
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {
                "latitude": -34.0362,
                "longitude": 23.0471,
                "address": "Knysna, South Africa",
            },
        )(),
        type(
            "Location",
            (object,),
            {
                "latitude": -29.0852,
                "longitude": 26.1596,
                "address": "Bloemfontein, South Africa",
            },
        )(),
        type(
            "Location",
            (object,),
            {
                "latitude": 25.276987,
                "longitude": 55.296249,
                "address": "Dubai, United Arab Emirates",
            },
        )(),
    ]

    data = [
        {"place_name": "Knysna", "start_date": "2024-10-15", "end_date": "2024-10-16"},
        {
            "place_name": "Bloemfontein",
            "start_date": "2024-10-15",
            "end_date": "2024-10-16",
        },
        {"place_name": "Dubai", "start_date": "2024-10-15", "end_date": "2024-10-16"},
    ]

    response = api_client.post("/api/weather/", data, format="json")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data[0]["place_name"] == "Knysna"
    assert response_data[1]["place_name"] == "Bloemfontein"
    assert response_data[2]["place_name"] == "Dubai"
    assert response_data[0]["weather_data"][0]["weather_description"] == "Partly cloudy"
    assert response_data[0]["weather_data"][1]["wind_direction"] == 101
    assert response_data[1]["weather_data"][0]["weather_description"] == "Partly cloudy"
    assert response_data[2]["weather_data"][1]["weather_description"] == "Overcast"


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_invalid_location(mock_geocode, mock_fetch_weather_data, api_client):
    # Simulate an error response for an invalid location
    mock_geocode.return_value = None
    mock_fetch_weather_data.side_effect = Exception("Invalid location")

    data = [
        {
            "place_name": "InvalidPlace",
            "start_date": "2024-10-16",
            "end_date": "2024-10-20",
        }
    ]

    response = api_client.post("/api/weather/", data, format="json")
    assert response.status_code == 400
    response_data = response.json()

    assert "error" in response_data
    assert response_data["error"] == "Geocoding failed for InvalidPlace"
