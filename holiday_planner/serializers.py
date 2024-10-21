from rest_framework import serializers


class WeatherDataSerializer(serializers.Serializer):
    place_name = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
