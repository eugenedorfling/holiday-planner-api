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

**Request Body (Length of Stay per location):**

```json
{
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
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

**Request Body (Dynamic/Suggested dates):**

```json
{
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
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

#### 4. Retrieve a Holiday Schedule

- **URL:** /api/schedule/{id}/
- **Method:** GET
- **Description:** Retrieves the details of a specific holiday schedule by its ID.

#### 5. Update a Holiday Schedule

- **URL:** /api/schedule/{id}/
- **Method:** PUT
- **Description:** Replaces the existing schedule with a new one. All fields must be provided.

**Request Body:**

```json
{
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "destinations_input": [
    {
      "place_name": "Berlin",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD"
    },
    {
      "place_name": "Amsterdam",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD"
    }
  ]
}
```

#### 6. Partial Update a Holiday Schedule

- **URL:** /api/schedule/{id}/
- **Method:** PATCH
- **Description:** Updates specific fields of a schedule. Only the fields provided in the request body will be updated.

**Request Body:**

```json
{
  "end_date": "YYYY-MM-DD",
  "destinations_input": [
    {
      "place_name": "Madrid",
      "length_of_stay": 2
    }
  ]
}
```

#### 7. Delete a Holiday Schedule

- **URL:** /api/schdule/{id}/
- **Method:** DELETE
- **Description:** Deletes a holiday schedule by its ID.

## Tasks Breakdown / Progress

1. ~~Create github repo, public~~
2. ~~Setup git locally~~
3. ~~Start ReadMe.md~~
4. Setup Dev Environment (Docker)
5. Create core django project
6. Create holiday_planner base app
7. Setup testing (pytest)
8. Automate testing (github actions)
9. Build Weather API (Third Party API)(single or multiple locations)
10. Build Holiday Scheduler API (with location duration options: dates, days, distributed)
    1. Add Basic Authentication
11. Build Schedule Weather API
12. Review and Improve
