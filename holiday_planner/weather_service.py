import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd

# Weather code description mapping based on WMO codes
WMO_WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Slight or moderate thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# Setup the Open-Meteo API client with caching and retries
cache_session = requests_cache.CachedSession(
    ".cache", expire_after=3600
)  # Cache for 1 hour
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def clean_weather_data(daily_dataframe):
    """
    Clean the weather data to return meaningful descriptions and rounded values.
    """
    daily_datadict = daily_dataframe.to_dict(orient="records")
    cleaned_data = []

    for daily_data in daily_datadict:
        # Get weather code description
        weather_code = daily_data["weather_code"]
        weather_description = WMO_WEATHER_CODE_MAP.get(weather_code, "Unknown")

        # Round floats to nearest integers
        temperature_max = round(daily_data["temperature_2m_max"])
        temperature_min = round(daily_data["temperature_2m_min"])
        uv_index_max = round(daily_data["uv_index_max"])
        precipitation_probability_max = round(
            daily_data["precipitation_probability_max"]
        )
        wind_speed_max = round(daily_data["wind_speed_10m_max"])
        wind_gusts_max = round(daily_data["wind_gusts_10m_max"])
        wind_direction_dominant = round(daily_data["wind_direction_10m_dominant"])

        # Create the cleaned daily weather entry
        cleaned_entry = {
            "date": daily_data["date"],
            "weather_code": weather_code,
            "weather_description": weather_description,
            "temperature_max": temperature_max,
            "temperature_min": temperature_min,
            "uv_index_max": uv_index_max,
            "precipitation_probability_max": precipitation_probability_max,
            "wind_speed_max": wind_speed_max,
            "wind_gusts_max": wind_gusts_max,
            "wind_direction": wind_direction_dominant,
        }

        cleaned_data.append(cleaned_entry)

    return cleaned_data


def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetch weather data from Open-Meteo API for the given coordinates and date range.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "uv_index_max",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
        ],
        "timezone": "Europe/Berlin",  # Adjust according to the destination
        "start_date": start_date,
        "end_date": end_date,
    }

    # Fetch response
    responses = openmeteo.weather_api(url, params=params)

    if not responses:
        raise ValueError("No weather data available")

    # Process first location (add for-loop for multiple locations if needed)
    response = responses[0]
    daily = response.Daily()

    # Collect daily data
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        ).strftime(
            "%Y-%m-%d"
        )  # Convert Timestamps to string format (ISO 8601)
    }
    daily_data["weather_code"] = daily.Variables(0).ValuesAsNumpy()
    daily_data["temperature_2m_max"] = daily.Variables(1).ValuesAsNumpy()
    daily_data["temperature_2m_min"] = daily.Variables(2).ValuesAsNumpy()
    daily_data["uv_index_max"] = daily.Variables(3).ValuesAsNumpy()
    daily_data["precipitation_probability_max"] = daily.Variables(4).ValuesAsNumpy()
    daily_data["wind_speed_10m_max"] = daily.Variables(5).ValuesAsNumpy()
    daily_data["wind_gusts_10m_max"] = daily.Variables(6).ValuesAsNumpy()
    daily_data["wind_direction_10m_dominant"] = daily.Variables(7).ValuesAsNumpy()

    # Create pandas dataframe
    daily_dataframe = pd.DataFrame(data=daily_data)
    return clean_weather_data(daily_dataframe)
