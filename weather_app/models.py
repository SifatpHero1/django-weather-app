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

    def __str__(self):
        return f"{self.user.username} preferences"
