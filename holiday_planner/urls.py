from django.urls import path
from .views import WeatherAPIView, UserList, UserDetail

urlpatterns = [
    path("users/", UserList.as_view()),
    path("users/<int:pk>/", UserDetail.as_view()),
    path("weather/", WeatherAPIView.as_view()),
]
