import requests
from django.conf import settings
import os


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')

    def get_api_key(self):
        """Get API key from environment or settings"""
        if not self.api_key:
            self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        return self.api_key

    def geocode_city(self, city_name, country_code='US', limit=5):
        """Convert city name to coordinates"""
        api_key = self.get_api_key()
        if not api_key:
            return None

        try:
            response = requests.get(
                self.GEO_URL,
                params={
                    'q': f"{city_name},{country_code}",
                    'limit': limit,
                    'appid': api_key
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'lat': data[0]['lat'],
                        'lon': data[0]['lon'],
                        'name': data[0]['name'],
                        'country': data[0].get('country', country_code)
                    }
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None

    def fetch_weather(self, lat, lon):
        """Fetch current weather data for coordinates"""
        api_key = self.get_api_key()
        if not api_key:
            return None

        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': api_key,
                    'units': 'metric'
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': round(data['wind'].get('speed', 0), 1),
                    'wind_deg': data['wind'].get('deg', 0),
                    'description': data['weather'][0]['description'].title(),
                    'icon_code': data['weather'][0]['icon']
                }
        except Exception as e:
            print(f"Weather fetch error: {e}")
        return None

    def get_weather_for_city(self, city_name, country_code='US'):
        """Get weather data for a city name"""
        geo = self.geocode_city(city_name, country_code)
        if geo:
            weather = self.fetch_weather(geo['lat'], geo['lon'])
            if weather:
                return {**geo, **weather}
        
        # Fallback to demo data if no API key or API fails
        return self.get_demo_weather(city_name, country_code)

    def get_demo_weather(self, city_name, country_code='US'):
        """Return demo weather data for testing without API key"""
        # Use consistent pseudo-random values based on city name
        import hashlib
        seed = int(hashlib.md5(city_name.encode()).hexdigest()[:8], 16)
        import random
        r = random.Random(seed)

        conditions = [
            ('Clear Sky', '01d', 22, 24),
            ('Few Clouds', '02d', 20, 22),
            ('Scattered Clouds', '03d', 18, 20),
            ('Broken Clouds', '04d', 16, 18),
            ('Light Rain', '10d', 17, 19),
            ('Moderate Rain', '09d', 15, 17),
            ('Overcast', '04d', 14, 16),
            ('Thunderstorm', '11d', 18, 20),
            ('Snow', '13d', -2, -4),
            ('Mist', '50d', 12, 13),
        ]
        
        condition = conditions[seed % len(conditions)]
        
        # Random but consistent coordinates
        lat = (seed % 180) - 90
        lon = ((seed * 7) % 360) - 180
        
        return {
            'lat': lat,
            'lon': lon,
            'name': city_name.split(',')[0].strip(),
            'country': country_code,
            'temperature': condition[2] + r.randint(-2, 2),
            'feels_like': condition[3],
            'humidity': r.randint(40, 90),
            'pressure': r.randint(1000, 1025),
            'wind_speed': round(r.uniform(1, 8), 1),
            'wind_deg': r.randint(0, 359),
            'description': condition[0],
            'icon_code': condition[1],
        }
