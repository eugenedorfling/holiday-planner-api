from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets, permissions
from geopy import Nominatim
from holiday_planner.models import Destination, HolidaySchedule
from holiday_planner.serializers import (
    WeatherDataSerializer,
    UserSerializer,
    HolidayScheduleSerializer,
)
from holiday_planner.weather_service import fetch_weather_data
from django.contrib.auth.models import User


class WeatherAPIView(APIView):
    def post(self, request):
        serializer = WeatherDataSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        geolocator = Nominatim(user_agent="holiday_planner")
        weather_results = []

        for location in serializer.validated_data:
            place_name = location.get("place_name")
            start_date = location.get("start_date")
            end_date = location.get("end_date")

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
                    start_date=start_date,
                    end_date=end_date,
                )
                weather_results.append(
                    {"place_name": place_name, "weather_data": weather_data}
                )
            else:
                return Response(
                    {"error": f"Geocoding failed for {place_name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(weather_results)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class HolidayScheduleViewSet(viewsets.ModelViewSet):
    queryset = HolidaySchedule.objects.prefetch_related("destinations__destination")
    serializer_class = HolidayScheduleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
