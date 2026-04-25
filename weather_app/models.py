from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2, default='US')
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name', 'country_code']
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name}, {self.country_code}"


class WeatherData(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, related_name='weather')
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    wind_deg = models.IntegerField()
    description = models.CharField(max_length=100)
    icon_code = models.CharField(max_length=10)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city.name}: {self.temperature}°C, {self.description}"


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    temperature_unit = models.CharField(max_length=10, default='celsius', choices=[
        ('celsius', 'Celsius'),
        ('fahrenheit', 'Fahrenheit'),
        ('kelvin', 'Kelvin'),
    ])
    wind_speed_unit = models.CharField(max_length=10, default='kmh', choices=[
        ('kmh', 'km/h'),
        ('ms', 'm/s'),
        ('mph', 'mph'),
    ])
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=30, help_text="Refresh interval in minutes")
    email_notifications = models.BooleanField(default=True, help_text="Receive email alerts")
    temperature_alert_threshold = models.FloatField(default=None, blank=True, null=True, help_text="Alert if temperature exceeds this value (Celsius)")

    def __str__(self):
        return f"{self.user.username} preferences"


class WeatherAlert(models.Model):
    """User-defined weather alerts"""
    ALERT_TYPES = [
        ('temp_above', 'Temperature Above'),
        ('temp_below', 'Temperature Below'),
        ('humidity_above', 'Humidity Above'),
        ('humidity_below', 'Humidity Below'),
        ('wind_above', 'Wind Speed Above'),
        ('pressure_above', 'Pressure Above'),
        ('pressure_below', 'Pressure Below'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_value = models.FloatField(help_text="Threshold value for the alert")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type} {self.threshold_value} for {self.city.name}"
