from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeatherAPIView, UserList, UserDetail, HolidayScheduleViewSet

router = DefaultRouter()
router.register(r"schedules", HolidayScheduleViewSet, basename="schedules")

urlpatterns = [
    path("", include(router.urls)),
    path("users/", UserList.as_view()),
    path("users/<int:pk>/", UserDetail.as_view()),
    path("weather/", WeatherAPIView.as_view()),
]
