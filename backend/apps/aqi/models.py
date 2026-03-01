from django.db import models
from django.conf import settings


class Station(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Kazakhstan")
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class AQIReading(models.Model):
    """Individual AQI sensor reading from a station."""

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="readings")
    recorded_at = models.DateTimeField()

    aqi = models.PositiveIntegerField()
    pm25 = models.FloatField(help_text="μg/m³")
    pm10 = models.FloatField(help_text="μg/m³")
    co2 = models.FloatField(help_text="ppm", null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)   # °C
    humidity = models.FloatField(null=True, blank=True)       # %

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["station", "-recorded_at"]),
            models.Index(fields=["-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.station.name} — AQI {self.aqi} @ {self.recorded_at:%Y-%m-%d %H:%M}"

    @property
    def aqi_category(self):
        if self.aqi <= 50:   return "Good"
        if self.aqi <= 100:  return "Moderate"
        if self.aqi <= 150:  return "Unhealthy for Sensitive Groups"
        if self.aqi <= 200:  return "Unhealthy"
        if self.aqi <= 300:  return "Very Unhealthy"
        return "Hazardous"


class AQIForecast(models.Model):
    """24-hour model prediction for a station."""

    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="forecasts")
    generated_at = models.DateTimeField(auto_now_add=True)
    forecast_hour = models.PositiveSmallIntegerField()   # 0–23
    predicted_aqi = models.PositiveIntegerField()
    confidence = models.FloatField(default=0.942)         # 0–1

    class Meta:
        ordering = ["generated_at", "forecast_hour"]
        unique_together = [["station", "generated_at", "forecast_hour"]]

    def __str__(self):
        return f"{self.station.name} forecast h+{self.forecast_hour} → AQI {self.predicted_aqi}"


class Alert(models.Model):
    """AQI threshold alert sent to a user."""

    class Severity(models.TextChoices):
        INFO    = "info",    "Info"
        WARNING = "warning", "Warning"
        DANGER  = "danger",  "Danger"

    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alerts")
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, related_name="alerts")
    severity  = models.CharField(max_length=10, choices=Severity.choices, default=Severity.WARNING)
    aqi_value = models.PositiveIntegerField()
    message   = models.TextField()
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert [{self.severity}] for {self.user.email} — AQI {self.aqi_value}"
