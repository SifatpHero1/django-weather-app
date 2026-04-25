from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import RegisterForm, LoginForm, AddCityForm, SettingsForm
from .models import City, WeatherData, UserPreference
from .services import WeatherService
import json


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default preferences
            UserPreference.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    cities = City.objects.filter(user=request.user).select_related('weather')
    weather_data = []
    
    # Get or create user preferences
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    for city in cities:
        if hasattr(city, 'weather'):
            weather_data.append({
                'city': city,
                'weather': city.weather,
                'unit': preference.temperature_unit,
            })

    context = {
        'weather_data': weather_data,
        'has_cities': cities.exists(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_city(request):
    # Popular city suggestions
    city_suggestions = [
        ('London', 'GB'),
        ('New York', 'US'),
        ('Tokyo', 'JP'),
        ('Paris', 'FR'),
        ('Sydney', 'AU'),
        ('Dubai', 'AE'),
        ('Singapore', 'SG'),
        ('Toronto', 'CA'),
        ('Mumbai', 'IN'),
        ('Dhaka', 'BD'),
    ]

    if request.method == 'POST':
        form = AddCityForm(request.POST, user=request.user)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            country_code = form.cleaned_data['country_code']

            # Fetch weather data
            service = WeatherService()
            result = service.get_weather_for_city(city_name, country_code)

            if result:
                # Create city
                city = City.objects.create(
                    user=request.user,
                    name=result['name'],
                    country_code=result['country'],
                    lat=result['lat'],
                    lon=result['lon']
                )

                # Create weather data
                WeatherData.objects.create(
                    city=city,
                    temperature=result['temperature'],
                    feels_like=result['feels_like'],
                    humidity=result['humidity'],
                    pressure=result['pressure'],
                    wind_speed=result['wind_speed'],
                    wind_deg=result['wind_deg'],
                    description=result['description'],
                    icon_code=result['icon_code']
                )

                messages.success(request, f'{city.name} added successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Could not fetch weather data for this city. Please check the city name and try again.')
    else:
        form = AddCityForm(user=request.user)

    context = {'form': form, 'city_suggestions': city_suggestions}
    return render(request, 'add_city.html', context)


@login_required
@require_POST
def remove_city(request, city_id):
    city = get_object_or_404(City, id=city_id, user=request.user)
    city_name = city.name
    city.delete()
    messages.success(request, f'{city_name} removed successfully.')
    return redirect('dashboard')


@login_required
def refresh_weather(request, city_id):
    """AJAX endpoint to refresh weather for a specific city"""
    city = get_object_or_404(City, id=city_id, user=request.user)
    service = WeatherService()
    result = service.get_weather_for_city(city.name, city.country_code)

    if result:
        # Update or create weather data
        weather, created = WeatherData.objects.update_or_create(
            city=city,
            defaults={
                'temperature': result['temperature'],
                'feels_like': result['feels_like'],
                'humidity': result['humidity'],
                'pressure': result['pressure'],
                'wind_speed': result['wind_speed'],
                'wind_deg': result['wind_deg'],
                'description': result['description'],
                'icon_code': result['icon_code'],
            }
        )
        return JsonResponse({'success': True, 'message': 'Weather updated'})
    return JsonResponse({'success': False, 'message': 'Failed to fetch weather'}, status=400)


@login_required
def settings_view(request):
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = SettingsForm(instance=preference)

    context = {'form': form}
    return render(request, 'settings.html', context)


def get_wind_direction(degrees):
    """Convert wind degrees to cardinal direction"""
    if degrees is None:
        return 'N/A'
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]
