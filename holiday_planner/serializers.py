from rest_framework import serializers
from django.contrib.auth.models import User
from holiday_planner.models import HolidaySchedule


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
