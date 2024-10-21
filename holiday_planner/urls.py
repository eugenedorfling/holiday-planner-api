from django.urls import path
from .views import HelloDjangoView

urlpatterns = [
    path("hello/", HelloDjangoView.as_view()),
]
