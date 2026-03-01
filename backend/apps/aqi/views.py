from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Max

from .models import Station, AQIReading, AQIForecast, Alert
from .serializers import (
    StationSerializer,
    AQIReadingSerializer,
    AQIForecastSerializer,
    AlertSerializer,
)


# ---------------------------------------------------------------------------
# Stations
# ---------------------------------------------------------------------------
class StationListView(generics.ListAPIView):
    """GET /api/aqi/stations/ — list all active monitoring stations"""
    queryset = Station.objects.filter(is_active=True)
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "city", "country"]


class StationDetailView(generics.RetrieveAPIView):
    """GET /api/aqi/stations/<id>/ — station detail + latest reading"""
    queryset = Station.objects.filter(is_active=True)
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        station = self.get_object()
        data = StationSerializer(station).data
        latest = station.readings.first()
        if latest:
            data["latest_reading"] = AQIReadingSerializer(latest).data
        return Response(data)


# ---------------------------------------------------------------------------
# AQI Readings
# ---------------------------------------------------------------------------
class AQIReadingListView(generics.ListAPIView):
    """GET /api/aqi/readings/?station=<id>&limit=24"""
    serializer_class = AQIReadingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = AQIReading.objects.select_related("station")
        station_id = self.request.query_params.get("station")
        if station_id:
            qs = qs.filter(station_id=station_id)
        return qs


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def dashboard_summary(request):
    """GET /api/aqi/summary/ — current snapshot for home dashboard"""
    stations = Station.objects.filter(is_active=True)
    latest_readings = []
    for st in stations:
        reading = st.readings.first()
        if reading:
            latest_readings.append(reading)

    if not latest_readings:
        return Response({"stations": [], "average_aqi": None, "max_aqi": None})

    aqi_values = [r.aqi for r in latest_readings]
    avg_aqi = round(sum(aqi_values) / len(aqi_values), 1)
    max_reading = max(latest_readings, key=lambda r: r.aqi)

    return Response({
        "station_count": stations.count(),
        "average_aqi": avg_aqi,
        "max_aqi": max_reading.aqi,
        "max_aqi_station": max_reading.station.name,
        "readings": AQIReadingSerializer(latest_readings, many=True).data,
        "timestamp": timezone.now(),
    })


# ---------------------------------------------------------------------------
# Forecasts
# ---------------------------------------------------------------------------
class ForecastListView(generics.ListAPIView):
    """GET /api/aqi/forecast/?station=<id>"""
    serializer_class = AQIForecastSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = AQIForecast.objects.select_related("station").order_by("forecast_hour")
        station_id = self.request.query_params.get("station")
        if station_id:
            qs = qs.filter(station_id=station_id)
        return qs


# ---------------------------------------------------------------------------
# User alerts
# ---------------------------------------------------------------------------
class AlertListView(generics.ListCreateAPIView):
    """GET /api/aqi/alerts/ — list own alerts; POST to create"""
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user).select_related("station")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/aqi/alerts/<id>/"""
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
