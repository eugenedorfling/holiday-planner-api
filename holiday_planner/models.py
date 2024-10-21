from django.db import models
from django.contrib.auth.models import User

# HolidaySchedule

# id: pk
# user: Link to Django Auth User
# start_date: date
# end_date: date
# created_at: datetime
# updated_at: datetime


class HolidaySchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.user.username} Schedule from {self.start_date} to {self.end_date}"
        )


# Destination

# id: pk
# name: varchar(255)
# country: varchar(255)
# longitude: float()
# latitude: float()
# created_at: datetime
# updated_at: datetime


class Destination(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


# ScheduleItem

# id: pk
# holiday_schedule: Link to HolidaySchedule
# destination: Link to Destination
# start_date: date(null) - to allow for flexible schedules
# end_date: date(null) - to allow for flexible schedules
# length_of_stay: int(null) - to allow for flexible schedules
# weather_data: json(null) - to allow weather data storage
# created_at: datetime
# updated_at: datetime


class ScheduleItem(models.Model):
    holiday_schedule = models.ForeignKey(
        HolidaySchedule, on_delete=models.CASCADE, related_name="destinations"
    )
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    # Now supports flexible dates per destination
    start_date = models.DateField(
        null=True, blank=True
    )  # Can be specific for a destination
    end_date = models.DateField(
        null=True, blank=True
    )  # Can be specific for a destination
    length_of_stay = models.PositiveIntegerField(
        null=True, blank=True
    )  # To calculate length of stay

    weather_data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.destination.name} ({self.start_date} - {self.end_date})"
