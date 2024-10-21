from datetime import datetime, timedelta

from django.contrib.auth.models import User
from geopy.geocoders import Nominatim
from holiday_planner.models import Destination, HolidaySchedule, ScheduleItem
from holiday_planner.weather_service import fetch_weather_data
from rest_framework import serializers

geolocator = Nominatim(user_agent="holiday_planner")


class WeatherDataSerializer(serializers.Serializer):
    place_name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class UserSerializer(serializers.ModelSerializer):
    schedules = serializers.PrimaryKeyRelatedField(
        many=True, queryset=HolidaySchedule.objects.all()
    )

    class Meta:
        model = User
        fields = ["id", "username", "schedules"]


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["name", "country", "latitude", "longitude"]


class ScheduleItemSerializer(serializers.ModelSerializer):
    # destination = DestinationSerializer()
    destination = serializers.CharField(source="destination.name")
    weather_data = serializers.JSONField()

    class Meta:
        model = ScheduleItem
        fields = [
            "destination",
            "start_date",
            "end_date",
            "length_of_stay",
            "weather_data",
        ]


class HolidayScheduleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    destinations = ScheduleItemSerializer(many=True, read_only=True)

    destinations_input = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()), write_only=True
    )

    class Meta:
        model = HolidaySchedule
        fields = [
            "id",
            "user",
            "start_date",
            "end_date",
            "destinations",
            "destinations_input",
        ]

    def create(self, validated_data):
        # Extract the nested destinations data
        destinations_input = validated_data.pop("destinations_input")

        # Create the holiday schedule
        holiday_schedule = HolidaySchedule.objects.create(**validated_data)

        current_start_date = validated_data["start_date"]
        current_end_date = validated_data["end_date"]

        # Calculate total days of the holiday
        total_days = (validated_data["end_date"] - validated_data["start_date"]).days

        # Count destinations without specific dates to calculate even distribution
        flexible_destinations = [
            d
            for d in destinations_input
            if not d.get("start_date") and not d.get("length_of_stay")
        ]

        if flexible_destinations:
            # Evenly distribute stay across destinations with no specific dates
            days_per_destination = total_days // len(flexible_destinations)
            extra_days = total_days % len(flexible_destinations)

        # Create each destination and associate it with the schedule
        for destination in destinations_input:
            place_name = destination.get("place_name")
            start_date = (
                datetime.strptime(destination.get("start_date"), "%Y-%m-%d").date()
                if destination.get("start_date")
                else None
            )

            end_date = (
                datetime.strptime(destination.get("end_date"), "%Y-%m-%d").date()
                if destination.get("end_date")
                else None
            )

            length_of_stay = destination.get("length_of_stay")

            # If no specific start/end date, calculate based on even distribution or length of stay
            if not start_date and not length_of_stay and flexible_destinations:
                if extra_days > 0:
                    adjusted_days = days_per_destination + 1
                    extra_days -= 1
                else:
                    adjusted_days = days_per_destination
                # Assign dates based on even distribution
                start_date = current_start_date
                end_date = current_start_date + timedelta(days=adjusted_days)
                current_start_date = end_date
                length_of_stay = days_per_destination

            elif length_of_stay and not start_date:
                # Calculate end_date from length_of_stay
                start_date = current_start_date
                end_date = start_date + timedelta(days=int(length_of_stay) - 1)
                current_start_date = end_date

            if current_start_date > current_end_date or start_date > current_end_date:
                raise serializers.ValidationError(
                    f"The destination {place_name} has a holiday start date {current_start_date} or start date {start_date} that is after the holiday end date {current_end_date}."
                )
            elif start_date > end_date:
                raise serializers.ValidationError(
                    f"The destination {place_name} has a start date {start_date} that is after the end date {end_date}."
                )

            # GeoCode the Place name
            location = geolocator.geocode(place_name)
            if location:
                # Check if destination exists otherwise create it
                destination, created = Destination.objects.get_or_create(
                    name=place_name,
                    defaults={
                        "country": location.address.split(", ")[-1].strip(),
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                    },
                )

                # Fetch weather data for the destination
                weather_data = fetch_weather_data(
                    latitude=destination.latitude,
                    longitude=destination.longitude,
                    start_date=start_date + timedelta(days=1),
                    end_date=end_date + timedelta(days=1),
                )

                # Create ScheduleItem with the provided dates or calculated ones
                ScheduleItem.objects.create(
                    holiday_schedule=holiday_schedule,
                    destination=destination,
                    start_date=start_date,
                    end_date=end_date,
                    length_of_stay=length_of_stay,
                    weather_data=weather_data,  # .to_dict(
                    #    orient="records"
                    # ),  # Save the weather data as JSON
                )
            else:
                raise serializers.ValidationError(
                    f"Geocoding failed for '{place_name}'"
                )

        return holiday_schedule

    def update(self, instance, validated_data):
        destinations_data = validated_data.pop("destinations_input", None)

        # Update the schedule dates
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.end_date = validated_data.get("end_date", instance.end_date)
        instance.save()

        if destinations_data:
            # Update destinations and schedule items
            instance.destinations.all().delete()  # Delete all current schedule items
            current_start_date = instance.start_date
            current_end_date = instance.end_date
            total_days = (current_end_date - current_start_date).days

            # Handle re-creating the destinations with updated data
            for destination in destinations_data:
                place_name = destination.get("place_name")
                start_date = (
                    datetime.strptime(destination.get("start_date"), "%Y-%m-%d").date()
                    if destination.get("start_date")
                    else None
                )
                end_date = (
                    datetime.strptime(destination.get("end_date"), "%Y-%m-%d").date()
                    if destination.get("end_date")
                    else None
                )
                length_of_stay = destination.get("length_of_stay")

                if not start_date and length_of_stay:
                    start_date = current_start_date
                    end_date = start_date + timedelta(days=int(length_of_stay) - 1)
                    current_start_date = end_date

                # Geocode and fetch the weather data as before
                location = geolocator.geocode(place_name)
                if location:
                    destination_obj, created = Destination.objects.get_or_create(
                        name=place_name,
                        defaults={
                            "country": location.address.split(", ")[-1].strip(),
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                        },
                    )

                    weather_data = fetch_weather_data(
                        latitude=destination_obj.latitude,
                        longitude=destination_obj.longitude,
                        start_date=start_date,
                        end_date=end_date,
                    )

                    # Recreate the schedule item
                    ScheduleItem.objects.create(
                        holiday_schedule=instance,
                        destination=destination_obj,
                        start_date=start_date,
                        end_date=end_date,
                        length_of_stay=length_of_stay,
                        weather_data=weather_data,
                    )
        return instance
