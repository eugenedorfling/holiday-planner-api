# Holiday Planner API - Coding Challenge

## Project Instructions

A company is building a holiday planner. Customers can choose a sequence of destinations as a schedule, taking the weather at each location into account.

### Task Description

- Build an API for a frontend that meets minimum requirements.
- Build the project with listed technologies.
- Limit implementation to 3 hours.

### Tech Stack Requirements

- django
- django-rest-framework
- database: ideally postgres or sqlite
- docker
- connection to a third party api [open-meteo.com](https://open-meteo.com/en/docs)
- automated tests

## Project Overview

The Holiday Planner API allows users to plan a holiday by selecting a series of destinations and retrieving relevant weather data for each location. The API integrates with third-party weather services to provide weather forecasts based on travel dates and destinations. This mini-project was built as part of a coding challenge, focusing on delivering key functionality with an emphasis on simplicity and code clarity within a limited timeframe.

## Key Features

- Create, view, edit, and delete holiday schedules.
- Add destinations by place name, including flexible options such as specific start/end dates or lengths of stay.
- Retrieve weather data for multiple locations based on user travel dates.
- Automatic geocoding of destination names to fetch latitude and longitude.
- Automated tests for critical functionalities.

## High-Level Design

### MVP User Stories

1.  As a customer I can view weather information at a location over a period of time so I can have a quick look at weather conditions for a specific location and date range.
2.  As a customer I can view weather information for multiple locations over a period of time so I can compare them.
3.  As a customer I can create and save a holiday schedule that includes locations and visit dates or length of visit so I can review the schedule along with weather conditions aligned with my schedule locations and dates.
4.  As a customer I can view weather information based on my schedule dates and locations.
5.  As a customer I can change/edit/delete schedule information (locations or dates).

### Extra User Stories

1. As a customer I can view a recommended schedule with best possible weather conditions given a schedule, start, and end dates along with a list of locations so I can have the best weather on my holiday.

### Data Models

We need data models to keep track of customer schedules and their schedule destinations along with relative weather data for each location. A destination should also be saved in order to be linked to a schedule and limit geo-coding api calls.

#### HolidaySchedule

- id: pk
- user: Link to Django Auth User
- start_date: date
- end_date: date
- created_at: datetime
- updated_at: datetime

#### Destination

- id: pk
- name: varchar(255)
- country: varchar(255)
- longitude: float()
- latitude: float()
- created_at: datetime
- updated_at: datetime

#### ScheduleItem

- id: pk
- holiday_schedule: Link to HolidaySchedule
- destination: Link to Destination
- start_date: date(null) - to allow for flexible schedules
- end_date: date(null) - to allow for flexible schedules
- length_of_stay: int(null) - to allow for flexible schedules
- weather_data: json(null) - to allow weather data storage
- created_at: datetime
- updated_at: datetime

### API Endpoints

#### 1. Retrieve Weather Information for a Location

- **URL:** /api/weather/
- **Method:** POST
- **Description:** Fetches weather information for a given destination and period.

**Request Body:**

```json
[
  {
    "place_name": "Paris",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }
]
```

**Response (200 OK):**

```json
[
  {
    "place_name": "Paris",
    "weather_data": [
      {
        "date": "YYYY-MM-DD",
        "weather_code": 80.0,
        "weather_description": "Slight rain showers",
        "temperature_max": 19,
        "temperature_min": 13,
        "uv_index_max": 2,
        "precipitation_probability_max": 13,
        "wind_speed_max": 16,
        "wind_gusts_max": 33,
        "wind_direction": 188
      },
      {
        "date": "YYYY-MM-DD",
        "weather_code": 80.0,
        "weather_description": "Slight rain showers",
        "temperature_max": 20,
        "temperature_min": 13,
        "uv_index_max": 3,
        "precipitation_probability_max": 63,
        "wind_speed_max": 19,
        "wind_gusts_max": 42,
        "wind_direction": 207
      }
    ]
  }
]
```

#### 2. Retrieve Weather Information for Multiple Locations

- **URL:** /api/weather/
- **Method:** POST
- **Description:** Fetches weather information for a given list of destinations. It can handle multiple locations at once.

**Request Body:**

```json
[
  {
    "place_name": "Paris",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  },
  {
    "place_name": "London",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }
]
```

**Response (200 OK):**

```json
[
  {
    "place_name": "Paris",
    "weather_data": [
      {
        "date": "YYYY-MM-DD",
        "weather_code": 80.0,
        "weather_description": "Slight rain showers",
        "temperature_max": 19,
        "temperature_min": 13,
        "uv_index_max": 2,
        "precipitation_probability_max": 13,
        "wind_speed_max": 16,
        "wind_gusts_max": 33,
        "wind_direction": 188
      }
    ]
  },
  {
    "place_name": "London",
    "weather_data": [
      {
        "date": "YYYY-MM-DD",
        "weather_code": 61.0,
        "weather_description": "Slight rain",
        "temperature_max": 18,
        "temperature_min": 11,
        "uv_index_max": 0,
        "precipitation_probability_max": 88,
        "wind_speed_max": 25,
        "wind_gusts_max": 54,
        "wind_direction": 201
      }
    ]
  }
]
```

#### 3. Create a Holiday Schedule

- **URL:** /api/schedule/
- **Method:** POST
- **Description:** Creates a new holiday schedule with a list of destinations and relative weather data. Destinations can include specific start/end dates or a length of stay at each location. Only `place_name` is required to allow for dynamic or suggested schedules.

**Request Body (Specific Start/End Dates):**

```json
{
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "destinations_input": [
    {
      "place_name": "Paris",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD"
    },
    {
      "place_name": "London",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD"
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "user": "admin",
  "start_date": "2024-10-25",
  "end_date": "2024-10-26",
  "destinations": [
    {
      "destination": "Paris",
      "start_date": "2024-10-25",
      "end_date": "2024-10-26",
      "length_of_stay": null,
      "weather_data": [
        {
          "date": "2024-10-25",
          "uv_index_max": 2,
          "weather_code": 3.0,
          "wind_direction": 227,
          "wind_gusts_max": 23,
          "wind_speed_max": 9,
          "temperature_max": 14,
          "temperature_min": 8,
          "weather_description": "Overcast",
          "precipitation_probability_max": 28
        },
        {
          "date": "2024-10-26",
          "uv_index_max": 2,
          "weather_code": 3.0,
          "wind_direction": 212,
          "wind_gusts_max": 33,
          "wind_speed_max": 13,
          "temperature_max": 16,
          "temperature_min": 7,
          "weather_description": "Overcast",
          "precipitation_probability_max": 17
        }
      ]
    },
    {
      "destination": "London",
      "start_date": "2024-10-26",
      "end_date": "2024-10-27",
      "length_of_stay": null,
      "weather_data": [
        {
          "date": "2024-10-26",
          "uv_index_max": 1,
          "weather_code": 61.0,
          "wind_direction": 226,
          "wind_gusts_max": 55,
          "wind_speed_max": 23,
          "temperature_max": 15,
          "temperature_min": 10,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 20
        },
        {
          "date": "2024-10-27",
          "uv_index_max": 2,
          "weather_code": 80.0,
          "wind_direction": 267,
          "wind_gusts_max": 62,
          "wind_speed_max": 24,
          "temperature_max": 15,
          "temperature_min": 9,
          "weather_description": "Slight rain showers",
          "precipitation_probability_max": 30
        }
      ]
    }
  ]
}
```

**Request Body (Length of Stay per location):**

```json
{
  "start_date": "2024-10-20",
  "end_date": "2024-10-24",
  "destinations_input": [
    {
      "place_name": "Paris",
      "length_of_stay": 2
    },
    {
      "place_name": "London",
      "length_of_stay": 2
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "user": "admin",
  "start_date": "2024-10-20",
  "end_date": "2024-10-24",
  "destinations": [
    {
      "destination": "Paris",
      "start_date": "2024-10-20",
      "end_date": "2024-10-21",
      "length_of_stay": 2,
      "weather_data": [
        {
          "date": "2024-10-20",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 219,
          "wind_gusts_max": 41,
          "wind_speed_max": 16,
          "temperature_max": 20,
          "temperature_min": 13,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 83
        },
        {
          "date": "2024-10-21",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 295,
          "wind_gusts_max": 25,
          "wind_speed_max": 11,
          "temperature_max": 17,
          "temperature_min": 10,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 60
        }
      ]
    },
    {
      "destination": "London",
      "start_date": "2024-10-21",
      "end_date": "2024-10-22",
      "length_of_stay": 2,
      "weather_data": [
        {
          "date": "2024-10-21",
          "uv_index_max": 2,
          "weather_code": 3.0,
          "wind_direction": 230,
          "wind_gusts_max": 36,
          "wind_speed_max": 15,
          "temperature_max": 16,
          "temperature_min": 9,
          "weather_description": "Overcast",
          "precipitation_probability_max": 10
        },
        {
          "date": "2024-10-22",
          "uv_index_max": 3,
          "weather_code": 3.0,
          "wind_direction": 195,
          "wind_gusts_max": 27,
          "wind_speed_max": 12,
          "temperature_max": 17,
          "temperature_min": 10,
          "weather_description": "Overcast",
          "precipitation_probability_max": 0
        }
      ]
    }
  ]
}
```

**Request Body (Dynamic/Suggested dates):**

```json
{
  "start_date": "2024-10-20",
  "end_date": "2024-10-21",
  "destinations_input": [
    {
      "place_name": "Paris"
    },
    {
      "place_name": "London"
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 3,
  "user": "admin",
  "start_date": "2024-10-20",
  "end_date": "2024-10-21",
  "destinations": [
    {
      "destination": "Paris",
      "start_date": "2024-10-20",
      "end_date": "2024-10-21",
      "length_of_stay": 0,
      "weather_data": [
        {
          "date": "2024-10-20",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 219,
          "wind_gusts_max": 41,
          "wind_speed_max": 16,
          "temperature_max": 20,
          "temperature_min": 13,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 83
        },
        {
          "date": "2024-10-21",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 295,
          "wind_gusts_max": 25,
          "wind_speed_max": 11,
          "temperature_max": 17,
          "temperature_min": 10,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 60
        }
      ]
    },
    {
      "destination": "London",
      "start_date": "2024-10-21",
      "end_date": "2024-10-21",
      "length_of_stay": 0,
      "weather_data": [
        {
          "date": "2024-10-21",
          "uv_index_max": 2,
          "weather_code": 3.0,
          "wind_direction": 230,
          "wind_gusts_max": 36,
          "wind_speed_max": 15,
          "temperature_max": 16,
          "temperature_min": 9,
          "weather_description": "Overcast",
          "precipitation_probability_max": 10
        }
      ]
    }
  ]
}
```

#### 4. Retrieve a Holiday Schedule

- **URL:** /api/schedule/{id}/
- **Method:** GET
- **Description:** Retrieves the details of a specific holiday schedule by its ID.

**Response (201 Created):**

```json
{
  "id": 2,
  "user": "admin",
  "start_date": "2024-10-20",
  "end_date": "2024-10-24",
  "destinations": [
    {
      "destination": "Paris",
      "start_date": "2024-10-20",
      "end_date": "2024-10-21",
      "length_of_stay": 2,
      "weather_data": [
        {
          "date": "2024-10-20",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 219,
          "wind_gusts_max": 41,
          "wind_speed_max": 16,
          "temperature_max": 20,
          "temperature_min": 13,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 83
        },
        {
          "date": "2024-10-21",
          "uv_index_max": 3,
          "weather_code": 61.0,
          "wind_direction": 295,
          "wind_gusts_max": 25,
          "wind_speed_max": 11,
          "temperature_max": 17,
          "temperature_min": 10,
          "weather_description": "Slight rain",
          "precipitation_probability_max": 60
        }
      ]
    },
    {
      "destination": "London",
      "start_date": "2024-10-21",
      "end_date": "2024-10-22",
      "length_of_stay": 2,
      "weather_data": [
        {
          "date": "2024-10-21",
          "uv_index_max": 2,
          "weather_code": 3.0,
          "wind_direction": 230,
          "wind_gusts_max": 36,
          "wind_speed_max": 15,
          "temperature_max": 16,
          "temperature_min": 9,
          "weather_description": "Overcast",
          "precipitation_probability_max": 10
        },
        {
          "date": "2024-10-22",
          "uv_index_max": 3,
          "weather_code": 3.0,
          "wind_direction": 195,
          "wind_gusts_max": 27,
          "wind_speed_max": 12,
          "temperature_max": 17,
          "temperature_min": 10,
          "weather_description": "Overcast",
          "precipitation_probability_max": 0
        }
      ]
    }
  ]
}
```

#### 5. Update a Holiday Schedule

- **URL:** /api/schedule/{id}/
- **Method:** PUT
- **Description:** Replaces the existing schedule with a new one. All fields must be provided.

**Request Body:**

```json
{
  "start_date": "2024-10-17",
  "end_date": "2024-10-19",
  "destinations_input": [
    {
      "place_name": "Berlin",
      "start_date": "2024-10-17",
      "end_date": "2024-10-18"
    },
    {
      "place_name": "Amsterdam",
      "start_date": "2024-10-18",
      "end_date": "2024-10-19"
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "id": 3,
  "user": "admin",
  "start_date": "2024-10-20",
  "end_date": "2024-10-22",
  "destinations": [
    {
      "destination": "Madrid",
      "start_date": "2024-10-21",
      "end_date": "2024-10-22",
      "length_of_stay": null,
      "weather_data": [
        {
          "date": "2024-10-20",
          "uv_index_max": 4,
          "weather_code": 45.0,
          "wind_direction": 44,
          "wind_gusts_max": 14,
          "wind_speed_max": 5,
          "temperature_max": 23,
          "temperature_min": 11,
          "weather_description": "Fog",
          "precipitation_probability_max": 0
        },
        {
          "date": "2024-10-21",
          "uv_index_max": 4,
          "weather_code": 3.0,
          "wind_direction": 41,
          "wind_gusts_max": 33,
          "wind_speed_max": 13,
          "temperature_max": 21,
          "temperature_min": 14,
          "weather_description": "Overcast",
          "precipitation_probability_max": 8
        }
      ]
    }
  ]
}
```

#### 7. Delete a Holiday Schedule

- **URL:** /api/schdule/{id}/
- **Method:** DELETE
- **Description:** Deletes a holiday schedule by its ID.

**Response (201 Created)**

## Tasks Breakdown / Progress

1. ~~Create github repo, public~~
2. ~~Setup git locally~~
3. ~~Start ReadMe.md~~
4. ~~Setup Dev Environment (Docker)~~
5. ~~Create core django project~~
6. ~~Create holiday_planner base app~~
7. ~~Setup testing (pytest)~~
8. ~~Automate testing (github actions)~~
9. ~~Build Weather API (Third Party API)(single or multiple locations)~~
10. ~~Build Holiday Scheduler API (with location duration options: dates, days, distributed)~~
    1. ~~Add Basic Authentication~~
11. Review and Improve
