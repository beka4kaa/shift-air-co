from django.contrib import admin
from .models import Station, AQIReading, AQIForecast, Alert


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "latitude", "longitude", "is_active")
    list_filter = ("is_active", "country", "city")
    search_fields = ("name", "city")


@admin.register(AQIReading)
class AQIReadingAdmin(admin.ModelAdmin):
    list_display = ("station", "recorded_at", "aqi", "pm25", "pm10", "co2")
    list_filter = ("station__city",)
    search_fields = ("station__name",)
    date_hierarchy = "recorded_at"


@admin.register(AQIForecast)
class AQIForecastAdmin(admin.ModelAdmin):
    list_display = ("station", "generated_at", "forecast_hour", "predicted_aqi", "confidence")
    list_filter = ("station__city",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("user", "station", "severity", "aqi_value", "is_read", "created_at")
    list_filter = ("severity", "is_read")
    search_fields = ("user__email", "station__name")
