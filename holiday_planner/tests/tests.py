import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from holiday_planner.models import (
    HolidaySchedule,
    ScheduleItem,
    Destination,
)

# # # # # # # # # # # #
#      FIXTURES       #
# # # # # # # # # # # #


# Create a test user fixture
@pytest.fixture
def user(db):
    # Create and return a user object
    return User.objects.create_user(username="testuser", password="testpassword")


# Create an API client fixture
@pytest.fixture
def api_client(user):
    client = APIClient()
    client.login(username=user.username, password="testpassword")
    return client


@pytest.fixture
def holiday_schedule(user):
    schedule = HolidaySchedule.objects.create(
        user=user, start_date="2024-10-20", end_date="2024-10-23"
    )
    # Create some initial destinations for the schedule
    destination_1 = Destination.objects.create(
        name="Paris", country="France", latitude=48.8566, longitude=2.3522
    )
    destination_2 = Destination.objects.create(
        name="London", country="UK", latitude=51.5074, longitude=-0.1278
    )

    ScheduleItem.objects.create(
        holiday_schedule=schedule,
        destination=destination_1,
        start_date="2024-10-20",
        end_date="2024-10-21",
    )
    ScheduleItem.objects.create(
        holiday_schedule=schedule,
        destination=destination_2,
        start_date="2024-10-21",
        end_date="2024-10-23",
    )

    return schedule


# # # # # # # # # # #
# WEATHER API TESTS #
# # # # # # # # # # #


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


# # # # # # # # # # # #
# SCHEDULES API TESTS #
# # # # # # # # # # # #


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_create_holiday_schedule_with_defined_dates(
    mock_geocode, mock_fetch_weather_data, api_client
):
    # Mock the weather data response
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-23",
            "weather_code": 2.0,
            "weather_description": "Sunny",
            "temperature_max": 25,
            "temperature_min": 15,
            "uv_index_max": 7,
            "precipitation_probability_max": 0,
            "wind_speed_max": 10,
            "wind_gusts_max": 20,
            "wind_direction": 270,
        },
        {
            "date": "2024-10-24",
            "weather_code": 3.0,
            "weather_description": "Overcast",
            "temperature_max": 20,
            "temperature_min": 12,
            "uv_index_max": 5,
            "precipitation_probability_max": 10,
            "wind_speed_max": 15,
            "wind_gusts_max": 25,
            "wind_direction": 260,
        },
        {
            "date": "2024-10-25",
            "weather_code": 1.0,
            "weather_description": "Rainy",
            "temperature_max": 18,
            "temperature_min": 10,
            "uv_index_max": 4,
            "precipitation_probability_max": 80,
            "wind_speed_max": 20,
            "wind_gusts_max": 35,
            "wind_direction": 250,
        },
    ]

    # Mock the geocoding response
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "address": "Paris, France",
            },
        )(),
        type(
            "Location",
            (object,),
            {
                "latitude": 51.5074,
                "longitude": -0.1278,
                "address": "London, UK",
            },
        )(),
        type(
            "Location",
            (object,),
            {
                "latitude": 52.5200,
                "longitude": 13.4050,
                "address": "Berlin, Germany",
            },
        )(),
    ]

    data = {
        "start_date": "2024-10-23",
        "end_date": "2024-10-26",
        "destinations_input": [
            {
                "place_name": "Paris",
                "start_date": "2024-10-23",
                "end_date": "2024-10-24",
            },
            {
                "place_name": "London",
                "start_date": "2024-10-24",
                "end_date": "2024-10-25",
            },
            {
                "place_name": "Berlin",
                "start_date": "2024-10-25",
                "end_date": "2024-10-26",
            },
        ],
    }

    response = api_client.post("/api/schedules/", data, format="json")
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["start_date"] == "2024-10-23"
    assert response_data["end_date"] == "2024-10-26"

    # Check if the destinations and weather data are returned as expected
    assert len(response_data["destinations"]) == 3
    assert response_data["destinations"][0]["destination"] == "Paris"
    assert response_data["destinations"][1]["destination"] == "London"
    assert response_data["destinations"][2]["destination"] == "Berlin"

    assert (
        response_data["destinations"][0]["weather_data"][0]["weather_description"]
        == "Fog"
    )
    assert (
        response_data["destinations"][1]["weather_data"][0]["weather_description"]
        == "Slight rain"
    )
    assert (
        response_data["destinations"][2]["weather_data"][0]["weather_description"]
        == "Slight rain"
    )


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_create_holiday_schedule_with_length_of_stay(
    mock_geocode, mock_fetch_weather_data, api_client
):
    # Mock geocoding responses for the locations
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {"latitude": 40.7128, "longitude": -74.0060, "address": "New York, USA"},
        )(),
        type(
            "Location",
            (object,),
            {"latitude": 42.3601, "longitude": -71.0589, "address": "Boston, USA"},
        )(),
        type(
            "Location",
            (object,),
            {"latitude": 25.7617, "longitude": -80.1918, "address": "Miami, USA"},
        )(),
    ]

    # Mock weather data for the length of stay
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-20",
            "weather_code": 2.0,
            "weather_description": "Partly cloudy",
            "temperature_max": 25,
            "temperature_min": 15,
            "wind_speed_max": 10,
        },
        {
            "date": "2024-10-21",
            "weather_code": 3.0,
            "weather_description": "Overcast",
            "temperature_max": 22,
            "temperature_min": 12,
            "wind_speed_max": 8,
        },
    ]

    data = {
        "start_date": "2024-10-20",
        "end_date": "2024-10-23",
        "destinations_input": [
            {"place_name": "New York", "length_of_stay": 2},
            {"place_name": "Boston", "length_of_stay": 2},
            {"place_name": "Miami", "length_of_stay": 2},
        ],
    }

    response = api_client.post("/api/schedules/", data, format="json")
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["start_date"] == "2024-10-20"
    assert response_data["end_date"] == "2024-10-23"


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_create_holiday_schedule_flexible(
    mock_geocode, mock_fetch_weather_data, api_client
):
    # Mock geocoding responses
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {"latitude": 33.7490, "longitude": -84.3880, "address": "Atlanta, USA"},
        )(),
        type(
            "Location",
            (object,),
            {"latitude": 29.7604, "longitude": -95.3698, "address": "Houston, USA"},
        )(),
        type(
            "Location",
            (object,),
            {"latitude": 34.0489, "longitude": -111.0937, "address": "Arizona, USA"},
        )(),
    ]

    # Mock weather data
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-20",
            "weather_code": 1.0,
            "weather_description": "Sunny",
            "temperature_max": 28,
            "temperature_min": 18,
            "wind_speed_max": 5,
        },
        {
            "date": "2024-10-21",
            "weather_code": 2.0,
            "weather_description": "Partly cloudy",
            "temperature_max": 26,
            "temperature_min": 17,
            "wind_speed_max": 8,
        },
    ]

    data = {
        "start_date": "2024-10-20",
        "end_date": "2024-10-26",
        "destinations_input": [
            {"place_name": "Atlanta"},
            {"place_name": "Huston"},
            {"place_name": "Arizona"},
        ],
    }

    response = api_client.post("/api/schedules/", data, format="json")
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["start_date"] == "2024-10-20"
    assert response_data["end_date"] == "2024-10-26"


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_patch_holiday_schedule(
    mock_geocode, mock_fetch_weather_data, api_client, holiday_schedule
):
    # Mock geocoding responses
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {"latitude": 48.8566, "longitude": 2.3522, "address": "Paris, France"},
        )(),
        type(
            "Location",
            (object,),
            {"latitude": 51.5074, "longitude": -0.1278, "address": "London, UK"},
        )(),
    ]

    # Mock weather data
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-25",
            "weather_code": 1.0,
            "weather_description": "Sunny",
            "temperature_max": 22,
            "temperature_min": 10,
            "wind_speed_max": 12,
        },
        {
            "date": "2024-10-26",
            "weather_code": 2.0,
            "weather_description": "Cloudy",
            "temperature_max": 20,
            "temperature_min": 12,
            "wind_speed_max": 15,
        },
    ]

    data = {
        "start_date": "2024-10-25",
        "end_date": "2024-10-28",
        "destinations_input": [
            {
                "place_name": "Paris",
                "start_date": "2024-10-25",
                "end_date": "2024-10-26",
            },
            {
                "place_name": "London",
                "start_date": "2024-10-26",
                "end_date": "2024-10-27",
            },
        ],
    }

    response = api_client.patch(
        f"/api/schedules/{holiday_schedule.id}/", data, format="json"
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["start_date"] == "2024-10-25"
    assert response_data["end_date"] == "2024-10-28"
    assert len(response_data["destinations"]) == 2
    assert response_data["destinations"][0]["destination"] == "Paris"


@pytest.mark.django_db
@patch("holiday_planner.views.fetch_weather_data")
@patch("geopy.Nominatim.geocode")
def test_put_holiday_schedule(
    mock_geocode, mock_fetch_weather_data, api_client, holiday_schedule
):
    # Mock geocoding responses
    mock_geocode.side_effect = [
        type(
            "Location",
            (object,),
            {"latitude": 52.5200, "longitude": 13.4050, "address": "Berlin, Germany"},
        )(),
        type(
            "Location",
            (object,),
            {
                "latitude": 52.3676,
                "longitude": 4.9041,
                "address": "Amsterdam, Netherlands",
            },
        )(),
    ]

    # Mock weather data
    mock_fetch_weather_data.return_value = [
        {
            "date": "2024-10-22",
            "weather_code": 3.0,
            "weather_description": "Overcast",
            "temperature_max": 17,
            "temperature_min": 10,
            "wind_speed_max": 20,
        },
        {
            "date": "2024-10-23",
            "weather_code": 2.0,
            "weather_description": "Partly cloudy",
            "temperature_max": 18,
            "temperature_min": 11,
            "wind_speed_max": 10,
        },
    ]

    data = {
        "start_date": "2024-10-22",
        "end_date": "2024-10-25",
        "destinations_input": [
            {
                "place_name": "Berlin",
                "start_date": "2024-10-22",
                "end_date": "2024-10-23",
            },
            {
                "place_name": "Amsterdam",
                "start_date": "2024-10-23",
                "end_date": "2024-10-25",
            },
        ],
    }

    response = api_client.put(
        f"/api/schedules/{holiday_schedule.id}/", data, format="json"
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["start_date"] == "2024-10-22"
    assert response_data["end_date"] == "2024-10-25"
    assert len(response_data["destinations"]) == 2
    assert response_data["destinations"][0]["destination"] == "Berlin"


@pytest.mark.django_db
def test_delete_holiday_schedule(api_client, holiday_schedule):
    response = api_client.delete(f"/api/schedules/{holiday_schedule.id}/")
    assert response.status_code == 204  # No content response for delete

    # Check if the schedule has been deleted
    get_response = api_client.get(f"/api/schedules/{holiday_schedule.id}/")
    assert get_response.status_code == 404  # The schedule should not exist anymore
