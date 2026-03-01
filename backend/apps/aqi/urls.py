from django.urls import path
from .views import (
    StationListView,
    StationDetailView,
    AQIReadingListView,
    ForecastListView,
    AlertListView,
    AlertDetailView,
    dashboard_summary,
)

urlpatterns = [
    path("stations/", StationListView.as_view(), name="station-list"),
    path("stations/<int:pk>/", StationDetailView.as_view(), name="station-detail"),
    path("readings/", AQIReadingListView.as_view(), name="reading-list"),
    path("forecast/", ForecastListView.as_view(), name="forecast-list"),
    path("summary/", dashboard_summary, name="dashboard-summary"),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
    path("alerts/<int:pk>/", AlertDetailView.as_view(), name="alert-detail"),
]
