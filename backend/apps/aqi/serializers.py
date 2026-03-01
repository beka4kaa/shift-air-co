from rest_framework import serializers
from .models import Station, AQIReading, AQIForecast, Alert


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "city", "country", "latitude", "longitude", "is_active")


class AQIReadingSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)
    aqi_category = serializers.ReadOnlyField()

    class Meta:
        model = AQIReading
        fields = (
            "id", "station", "station_name", "recorded_at",
            "aqi", "aqi_category", "pm25", "pm10", "co2",
            "temperature", "humidity",
        )


class AQIForecastSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = AQIForecast
        fields = ("id", "station", "station_name", "generated_at", "forecast_hour", "predicted_aqi", "confidence")


class AlertSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = Alert
        fields = ("id", "station", "station_name", "severity", "aqi_value", "message", "is_read", "created_at")
        read_only_fields = ("id", "created_at")
