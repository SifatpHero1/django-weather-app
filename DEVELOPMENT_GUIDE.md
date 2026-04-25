# WeatherApp - Beginner's Step-by-Step Development Guide

*This guide explains how this weather application was built, from start to finish. Perfect for beginners learning Django!*

---

## Table of Contents

1. [Project Planning](#1-project-planning)
2. [Setting Up Django](#2-setting-up-django)
3. [Building the Database](#3-building-the-database)
4. [Creating the Weather Service](#4-creating-the-weather-service)
5. [Building the Homepage](#5-building-the-homepage)
6. [User Authentication](#6-user-authentication)
7. [The Dashboard Page](#7-the-dashboard-page)
8. [Adding Cities Feature](#8-adding-cities-feature)
9. [Settings & Personalization](#9-settings--personalization)
10. [Smart Alerts System](#10-smart-alerts-system)
11. [Final Touches](#11-final-touches)
12. [How To Run The App](#12-how-to-run-the-app)

---

## 1. Project Planning

### What We Wanted to Build

A weather app that lets users:
- Track weather in multiple cities
- Customize temperature units (°C, °F, K)
- Get alerts when weather conditions change
- Simple, beautiful interface

### Pages We Needed

1. **Home Page** - Welcome page with feature highlights
2. **Register/Login** - User authentication
3. **Dashboard** - View all tracked cities' weather
4. **Add City** - Search and add new cities
5. **Settings** - Change preferences
6. **Alerts** - Manage weather notifications

### Tools We Used

- **Django** - Web framework (handles backend logic)
- **OpenWeatherMap API** - Free weather data source
- **SQLite** - Database (comes with Django)
- **Tailwind CSS** - Quick, pretty styling
- **Font Awesome** - Icons (clouds, sun, etc.)

---

## 2. Setting Up Django

### Step 2.1: Create the Project

```bash
# Create the Django project
django-admin startproject weather_project

# Create the main app
python manage.py startapp weather_app

# Create migrations (database setup)
python manage.py makemigrations
python manage.py migrate

# Create a superuser (admin access)
python manage.py createsuperuser
```

### Step 2.2: Project Structure

```
django_weather_app/
├── weather_project/        # Project settings
│   ├── settings.py        # Configuration (INSTALLED_APPS, DATABASE, etc.)
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # Deployment server config
├── weather_app/           # Our main app
│   ├── models.py         # Database tables (City, WeatherData, etc.)
│   ├── views.py          # Page logic (what to show)
│   ├── forms.py          # Forms for user input
│   ├── urls.py           # App-level URL routing
│   └── templates/        # HTML files
└── manage.py             # Start the server
```

### Step 2.3: Configure Settings

In `weather_project/settings.py`:

```python
# Add our app
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',      # User accounts
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weather_app',              # Our app!
]

# Tell Django where templates are
TEMPLATES = [{
    'DIRS': [BASE_DIR / 'weather_app' / 'templates'],
    ...
}]
```

---

## 3. Building the Database

### Step 3.1: The City Model

We needed to store:
- Which user added the city (relationship)
- City name and country code
- Coordinates (latitude/longitude) for API calls
- Whether it's their primary city

**File:** `weather_app/models.py`

```python
class City(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2, default='US')
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'name', 'country_code']
```

**Key Points:**
- `ForeignKey` links to User (one user can have many cities)
- `unique_together` prevents duplicate cities for one user
- `blank=True, null=True` allows fields to be optional

### Step 3.2: WeatherData Model

Stores the actual weather information for a city:

```python
class WeatherData(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    wind_deg = models.IntegerField()
    description = models.CharField(max_length=100)
    icon_code = models.CharField(max_length=10)  # e.g., "01d" for clear sky
    last_updated = models.DateTimeField(auto_now=True)
```

**Why `OneToOneField`?** Each city has exactly ONE weather record at a time. When we update weather, we replace this record.

### Step 3.3: UserPreference Model

Stores user settings:

```python
class UserPreference(models.Model):
    user = models.OneToOneField(User, related_name='preferences')
    temperature_unit = CharField(choices=['celsius', 'fahrenheit', 'kelvin'])
    wind_speed_unit = CharField(choices=['kmh', 'ms', 'mph'])
    auto_refresh = BooleanField(default=True)
    refresh_interval = IntegerField(default=30)  # minutes
```

### Step 3.4: WeatherAlert Model (Added Later)

For the Smart Alerts feature:

```python
class WeatherAlert(models.Model):
    ALERT_TYPES = [
        ('temp_above', 'Temperature Above'),
        ('temp_below', 'Temperature Below'),
        ('humidity_above', 'Humidity Above'),
        ('wind_above', 'Wind Speed Above'),
        ...
    ]

    user = ForeignKey(User)
    city = ForeignKey(City)
    alert_type = CharField(choices=ALERT_TYPES)
    threshold_value = FloatField()
    is_active = BooleanField(default=True)
```

---

## 4. Creating the Weather Service

### Step 4.1: The Problem

Django can't directly fetch data from the internet in models/views cleanly. We need a **service class** to handle all API communication.

**File:** `weather_app/services.py`

### Step 4.2: WeatherService Class

```python
class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')

    def get_api_key(self):
        if not self.api_key:
            self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        return self.api_key
```

### Step 4.3: Geocoding (City → Coordinates)

```python
def geocode_city(self, city_name, country_code='US', limit=5):
    """Convert 'London,GB' to latitude/longitude"""
    api_key = self.get_api_key()
    response = requests.get(
        self.GEO_URL,
        params={'q': f"{city_name},{country_code}", 'limit': limit, 'appid': api_key}
    )
    if response.status_code == 200:
        data = response.json()
        return {
            'lat': data[0]['lat'],
            'lon': data[0]['lon'],
            'name': data[0]['name'],
            'country': data[0].get('country', country_code)
        }
    return None
```

### Step 4.4: Fetching Weather Data

```python
def fetch_weather(self, lat, lon):
    """Get current weather for coordinates"""
    response = requests.get(
        self.BASE_URL,
        params={
            'lat': lat, 'lon': lon,
            'appid': api_key,
            'units': 'metric'  # Get Celsius by default
        }
    )
    if response.status_code == 200:
        data = response.json()
        return {
            'temperature': round(data['main']['temp'], 1),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind'].get('speed', 0), 1),
            'description': data['weather'][0]['description'].title(),
            'icon_code': data['weather'][0]['icon']  # e.g., "01d.png"
        }
```

### Step 4.5: Demo Mode (No API Key Required)

For testing without an API key:

```python
def get_demo_weather(self, city_name, country_code='US'):
    """Return consistent fake weather based on city name hash"""
    import hashlib, random
    seed = int(hashlib.md5(city_name.encode()).hexdigest()[:8], 16)
    r = random.Random(seed)

    # Pick condition based on hash (same city = same weather)
    conditions = [('Clear Sky', '01d', 22), ('Rain', '10d', 17), ...]
    condition = conditions[seed % len(conditions)]

    return {
        'temperature': condition[2] + r.randint(-2, 2),
        'description': condition[0],
        'icon_code': condition[1],
        ...
    }
```

---

## 5. Building the Homepage

### Step 5.1: The View

In `views.py`:

```python
def home(request):
    """Just render the landing page"""
    return render(request, 'home.html')
```

Very simple - no logic needed!

### Step 5.2: The Template

**File:** `weather_app/templates/home.html`

Uses **Template Inheritance** - extends `base.html`:

```html
{% extends 'base.html' %}

{% block title %}Home - WeatherApp{% endblock %}

{% block content %}
<div class="text-center py-20">
    <i class="fas fa-cloud-sun text-8xl"></i>
    <h1>Your Personal Weather Companion</h1>

    <!-- Two big buttons for logged-in vs guest -->
    {% if user.is_authenticated %}
        <a href="{% url 'dashboard' %}">Go to Dashboard</a>
    {% else %}
        <a href="{% url 'register' %}">Get Started Free</a>
        <a href="{% url 'login' %}">Sign In</a>
    {% endif %}

    <!-- Feature boxes (now clickable!) -->
    <div class="grid md:grid-cols-3 gap-6">
        <a href="{% url 'dashboard' %}" class="glass ...">
            <i class="fas fa-globe-americas"></i>
            <h3>Global Coverage</h3>
            <p>View weather in all your tracked cities worldwide.</p>
        </a>
        <a href="{% url 'alerts' %}" class="glass ...">
            <i class="fas fa-bell"></i>
            <h3>Smart Alerts</h3>
            ...
        </a>
        ...
    </div>
</div>
{% endblock %}
```

**Key Concept:**
- `{% extends 'base.html' %}` - Reuse the navbar and footer from base
- `{% block content %}` - Replace only the main section
- `{% url 'dashboard' %}` - Reverse URL lookup (don't hardcode paths!)

---

## 6. User Authentication

Django has built-in authentication. We just need forms and views.

### Step 6.1: Registration Form

**File:** `weather_app/forms.py`

```python
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
```

Extends Django's `UserCreationForm` (already handles password validation).

### Step 6.2: Login Form

```python
class LoginForm(AuthenticationForm):
    username = forms.CharField(...)
    password = forms.CharField(widget=forms.PasswordInput)
```

### Step 6.3: Registration View

```python
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default preferences for new user
            UserPreference.objects.create(user=user)
            login(request, user)  # Auto-login after register
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})
```

**Important:** Create `UserPreference` immediately so the user has settings.

### Step 6.4: Login View

```python
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
```

### Step 6.5: Templates

`register.html` and `login.html` extend `base.html` and display the forms:

```html
<form method="post" class="space-y-6">
    {% csrf_token %}
    {{ form.username }}
    {{ form.email }}
    {{ form.password1 }}
    {{ form.password2 }}
    <button type="submit">Sign Up</button>
</form>
```

**`{% csrf_token %}`** - Required for all POST forms in Django (security).

---

## 7. The Dashboard Page

### Step 7.1: Dashboard View

**File:** `weather_app/views.py`

```python
@login_required  # Must be logged in!
def dashboard(request):
    # Get all cities for this user (and their weather data)
    cities = City.objects.filter(user=request.user).select_related('weather')

    # Get user preferences
    preference = UserPreference.objects.get_or_create(user=request.user)

    weather_data = []
    for city in cities:
        if hasattr(city, 'weather'):  # Has weather data?
            weather_data.append({
                'city': city,
                'weather': city.weather,
                'unit': preference.temperature_unit
            })

    return render(request, 'dashboard.html', {
        'weather_data': weather_data,
        'has_cities': cities.exists()
    })
```

**`@login_required`** - Redirects to login if not authenticated.

**`select_related('weather')`** - Joins City and WeatherData in one query (faster).

### Step 7.2: Dashboard Template

**File:** `weather_app/templates/dashboard.html`

```html
{% if not has_cities %}
    <!-- Empty state - no cities yet -->
    <div class="glass rounded-2xl p-12 text-center">
        <h2>No Cities Yet</h2>
        <a href="{% url 'add_city' %}">Add Your First City</a>
    </div>
{% else %}
    <!-- Weather cards in a grid -->
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {% for item in weather_data %}
            <div class="glass rounded-2xl">
                <!-- City name and delete button -->
                <div class="...">
                    <h2>{{ item.city.name }}</h2>
                    <form method="post" action="{% url 'remove_city' item.city.id %}">
                        {% csrf_token %}
                        <button>Delete</button>
                    </form>
                </div>

                <!-- Weather details -->
                <div class="p-6">
                    <div class="text-5xl">{{ item.weather.temperature }}°C</div>
                    <img src="http://openweathermap.org/img/wn/{{ item.weather.icon_code }}@2x.png">

                    <!-- Humidity, wind, pressure boxes -->
                    <div class="grid grid-cols-2 gap-3">
                        <div><i class="fas fa-tint"></i> {{ item.weather.humidity }}%</div>
                        <div><i class="fas fa-wind"></i> {{ item.weather.wind_speed }} m/s</div>
                        ...
                    </div>

                    <!-- Refresh button -->
                    <form method="post" action="{% url 'refresh_weather' item.city.id %}">
                        {% csrf_token %}
                        <button>Refresh</button>
                    </form>
                </div>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

---

## 8. Adding Cities Feature

### Step 8.1: The AddCityForm

**File:** `weather_app/forms.py`

```python
class AddCityForm(forms.Form):
    city_name = forms.CharField(max_length=100, widget=forms.TextInput(...))
    country_code = forms.CharField(max_length=2, initial='US')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get user from view
        super().__init__(*args, **kwargs)

    def clean(self):
        # Check for duplicate city (case-insensitive)
        if City.objects.filter(
            user=self.user,
            name__iexact=city_name,
            country_code__iexact=country_code
        ).exists():
            raise forms.ValidationError("You already have this city.")
```

**Why in `clean()`?** Validation that needs both fields together goes here.

### Step 8.2: Add City View

```python
@login_required
def add_city(request):
    city_suggestions = [
        ('London', 'GB'), ('New York', 'US'), ('Tokyo', 'JP'), ...
    ]

    if request.method == 'POST':
        form = AddCityForm(request.POST, user=request.user)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            country_code = form.cleaned_data['country_code']

            # 1. Fetch weather from API
            service = WeatherService()
            result = service.get_weather_for_city(city_name, country_code)

            if result:
                # 2. Create City
                city = City.objects.create(
                    user=request.user,
                    name=result['name'],      # Normalized name from API
                    country_code=result['country'],
                    lat=result['lat'],
                    lon=result['lon']
                )

                # 3. Create WeatherData for that city
                WeatherData.objects.create(
                    city=city,
                    temperature=result['temperature'],
                    humidity=result['humidity'],
                    ...
                )

                messages.success(request, f'{city.name} added!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Could not fetch weather data.')
    else:
        form = AddCityForm(user=request.user)

    return render(request, 'add_city.html', {'form': form, 'city_suggestions': city_suggestions})
```

**Flow:**
1. User submits form → validate
2. Call weather API (with fallback to demo mode)
3. Create `City` record with coordinates
4. Create `WeatherData` record with current conditions
5. Redirect to dashboard

### Step 8.3: Add City Template

**File:** `weather_app/templates/add_city.html`

Shows:
- Form with city name and country code inputs
- Popular cities as clickable links (pre-fill form via URL params)
- Real-time validation messages

---

## 9. Settings & Personalization

### Step 9.1: SettingsForm

**File:** `weather_app/forms.py`

```python
class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['temperature_unit', 'wind_speed_unit', 'auto_refresh', 'refresh_interval']
        widgets = {
            'temperature_unit': forms.Select(choices=[...]),
            'refresh_interval': forms.NumberInput(attrs={'min': 5, 'max': 120})
        }
```

`ModelForm` - automatically creates form fields from model fields.

### Step 9.2: Settings View

```python
@login_required
def settings_view(request):
    # Get or create preference (first time user)
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated!')
            return redirect('settings')
    else:
        form = SettingsForm(instance=preference)

    return render(request, 'settings.html', {'form': form})
```

**`get_or_create`** - Returns existing preference or creates new one (prevents errors).

### Step 9.3: Settings Template

Dropdowns and checkboxes bound to the form. When saved, values update in database.

---

## 10. Smart Alerts System

### Step 10.1: Why Alerts Were Needed

Users wanted to know when:
- Temperature gets too hot/cold
- Humidity drops below a level
- Wind speed becomes dangerous

### Step 10.2: The Alert Model

```python
class WeatherAlert(models.Model):
    ALERT_TYPES = [
        ('temp_above', 'Temperature Above'),
        ('temp_below', 'Temperature Below'),
        ('humidity_above', 'Humidity Above'),
        ('humidity_below', 'Humidity Below'),
        ('wind_above', 'Wind Speed Above'),
        ('pressure_above', 'Pressure Above'),
        ('pressure_below', 'Pressure Below'),
    ]

    user = ForeignKey(User)
    city = ForeignKey(City)
    alert_type = CharField(choices=ALERT_TYPES)
    threshold_value = FloatField()  # e.g., 35.0 for "temp above 35°C"
    is_active = BooleanField(default=True)
    last_triggered = DateTimeField(blank=True, null=True)
```

### Step 10.3: AlertForm

```python
class AlertForm(forms.Form):
    city = forms.CharField(...)  # Must exist in user's dashboard
    alert_type = forms.ChoiceField(choices=WeatherAlert.ALERT_TYPES)
    threshold_value = forms.FloatField()

    def clean(self):
        # Verify city belongs to user
        if not City.objects.filter(user=self.user, name__iexact=city_name).exists():
            raise forms.ValidationError("Add this city to dashboard first!")
```

### Step 10.4: Alerts View

```python
@login_required
def alerts_view(request):
    alerts = WeatherAlert.objects.filter(user=request.user)

    if request.method == 'POST':
        form = AlertForm(request.POST, user=request.user)
        if form.is_valid():
            city = City.objects.get(user=request.user, name__iexact=city_name)
            WeatherAlert.objects.create(
                user=request.user,
                city=city,
                alert_type=form.cleaned_data['alert_type'],
                threshold_value=form.cleaned_data['threshold_value']
            )
            return redirect('alerts')

    return render(request, 'alerts.html', {'alerts': alerts, 'form': form})
```

### Step 10.5: Alert Checking When Weather Refreshes

```python
@login_required
def refresh_weather(request, city_id):
    city = get_object_or_404(City, id=city_id, user=request.user)
    service = WeatherService()
    result = service.get_weather_for_city(city.name, city.country_code)

    if result:
        # Update weather in database
        weather, created = WeatherData.objects.update_or_create(
            city=city, defaults={...}
        )

        # CHECK ALERTS!
        check_alerts_for_city(request, city, weather)

        return JsonResponse({'success': True})
```

**Alert Checking Function:**

```python
def check_alerts_for_city(request, city, weather):
    alerts = WeatherAlert.objects.filter(city=city, is_active=True)

    for alert in alerts:
        triggered = False

        if alert.alert_type == 'temp_above' and weather.temperature > alert.threshold_value:
            triggered = True
        elif alert.alert_type == 'temp_below' and weather.temperature < alert.threshold_value:
            triggered = True
        # ... check other types

        if triggered:
            alert.last_triggered = timezone.now()
            alert.save()

            # Store in session to show on next page load
            if 'recent_alerts' not in request.session:
                request.session['recent_alerts'] = []
            request.session['recent_alerts'].append({
                'city': city.name,
                'type': alert.get_alert_type_display(),
                'threshold': alert.threshold_value,
                'current_value': weather.temperature
            })
```

### Step 10.6: Displaying Alerts on Dashboard

In `dashboard.html`:

```html
{% if recent_alerts %}
    {% for alert in recent_alerts %}
        <div class="bg-yellow-500/20 ...">
            <strong>{{ alert.city }}</strong>: {{ alert.type }} breached!
            Current: {{ alert.current_value }}
        </div>
    {% endfor %}
{% endif %}
```

### Step 10.7: Managing Alerts

In `alerts.html`, each alert has:
- Pause/Resume button (toggles `is_active`)
- Delete button (deletes the alert)
- Shows when it last triggered

---

## 11. Final Touches

### Step 11.1: Navigation Updates

Added "Alerts" link to `base.html` navbar (visible only when logged in):

```html
{% if user.is_authenticated %}
    <a href="{% url 'dashboard' %}">Dashboard</a>
    <a href="{% url 'alerts' %}">Alerts</a>  <!-- New! -->
    <a href="{% url 'settings' %}">Settings</a>
{% endif %}
```

### Step 11.2: Connected Home Page to Features

Changed home page boxes from static `<div>` to clickable `<a>` tags:

```html
<a href="{% url 'dashboard' %}" class="glass ...">
    <h3>Global Coverage</h3>
    ...
</a>
<a href="{% url 'alerts' %}" class="glass ...">
    <h3>Smart Alerts</h3>
    ...
</a>
<a href="{% url 'settings' %}" class="glass ...">
    <h3>Personalized</h3>
    ...
</a>
```

### Step 11.3: URL Routing

**File:** `weather_app/urls.py`

```python
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_city/', views.add_city, name='add_city'),
    path('remove_city/<int:city_id>/', views.remove_city, name='remove_city'),
    path('refresh_weather/<int:city_id>/', views.refresh_weather, name='refresh_weather'),
    path('settings/', views.settings_view, name='settings'),
    path('alerts/', views.alerts_view, name='alerts'),                  # New
    path('alerts/delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),  # New
    path('alerts/toggle/<int:alert_id>/', views.toggle_alert, name='toggle_alert'),  # New
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
```

### Step 11.4: Database Migrations

After changing models:

```bash
# Create migration files
python manage.py makemigrations

# Apply to database
python manage.py migrate
```

This creates SQL commands to add new columns/tables.

---

## 12. How To Run The App

### Step 12.1: Prerequisites

1. **Python 3.9 or higher** installed
2. **OpenWeatherMap API key** (free):
   - Go to https://openweathermap.org/api
   - Sign up (free tier gives 1000 calls/day)
   - Copy your API key from dashboard

### Step 12.2: Install Dependencies

```bash
cd django_weather_app

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**`requirements.txt`** should contain:
```
Django==5.x
python-dotenv==1.x
requests==2.x
```

### Step 12.3: Configure API Key

Create `.env` file in `django_weather_app/` folder:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### Step 12.4: Run Database Migrations

```bash
python manage.py migrate
```

Creates tables for:
- `auth_user` (built-in Django users)
- `weather_app_city`
- `weather_app_weatherdata`
- `weather_app_userpreference`
- `weather_app_weatheralert`

### Step 12.5: Start Server

```bash
python manage.py runserver
```

Output:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
April 25, 2026 - 11:30:00
Django version 5.x, using settings 'weather_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 12.6: Open Browser

Go to: **http://127.0.0.1:8000/**

You'll see:
- **Home page** with 3 feature boxes
- Click "Get Started Free" → Register
- After login → Dashboard (empty, no cities yet)
- Click "Add City" → Enter a city (try "London, GB")
- See weather appear!
- Click "Smart Alerts" → Create an alert (e.g., temperature above 30)
- Click "Personalized" → Change units

---

## Common Beginner Questions

### Q: What's the difference between `models.py`, `views.py`, and `templates/`?

**`models.py`** - Database structure (like Excel columns):
```python
class City(models.Model):
    name = models.CharField()  # Column 1
    lat = models.FloatField()  # Column 2
```

**`views.py`** - Logic for each page (what data to fetch):
```python
def dashboard(request):
    cities = City.objects.all()  # Get all cities from DB
    return render(request, 'dashboard.html', {'cities': cities})
```

**`templates/`** - HTML files (what user sees):
```html
<h1>{{ cities.0.name }}</h1>  <!-- Renders: <h1>London</h1> -->
```

### Q: What does `@login_required` do?

It's a **decorator** that checks: "Is user logged in?" If NO → redirect to login page. If YES → show the page.

Applied to:
- `dashboard`
- `add_city`
- `settings_view`
- `alerts_view`

Public pages (no decorator):
- `home`
- `login`
- `register`

### Q: What's `POST` vs `GET`?

- **GET** - Just viewing a page (no changes)
  - `/dashboard/` → show dashboard
  - `/add_city/` → show form

- **POST** - Submitting a form (changes data)
  - `/add_city/` with form data → creates new city
  - `/refresh_weather/1/` → updates weather for city ID 1

In views:
```python
if request.method == 'POST':
    # Handle form submission
else:
    # Show empty form
```

### Q: What's `select_related('weather')`?

Django optimization. `City` has a `OneToOneField` to `WeatherData`.

Without `select_related`:
- Query 1: Get all cities for user (10 cities = 10 queries)
- Query 2: For each city, get its weather (10 more queries)
- Total: **11 queries**

With `select_related('weather')`:
- One JOIN query gets all cities + weather together
- Total: **1 query**

### Q: What's the `.env` file?

Stores secrets (API keys) outside code. Using `python-dotenv`:

```python
# services.py
import os
api_key = os.getenv('OPENWEATHER_API_KEY')
```

Load `.env` automatically in `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Q: How does the alert system work?

1. User creates alert: "London temp above 30°C"
2. Stored in `WeatherAlert` table
3. When user clicks "Refresh" on dashboard:
   - `refresh_weather` view fetches new weather
   - Calls `check_alerts_for_city(city, weather)`
   - Loops through user's active alerts for that city
   - If `weather.temp > 30`, marks alert as triggered
   - Stores message in `request.session` (temporary)
4. Dashboard displays yellow banner: "London: Temperature Above threshold breached!"

### Q: What's the difference between `redirect()` and `render()`?

- **`render(request, 'template.html', context)`**
  - Shows a page
  - Keeps current URL in browser
  - Example: After adding city successfully, show dashboard

- **`redirect('url_name')`**
  - Tells browser to go to a different URL
  - Changes URL in browser
  - Example: After form submit → redirect to prevent duplicate submission

**Post/Redirect/Get pattern:**
```
POST /add_city/  →  Save data  →  Redirect to /dashboard/
GET  /dashboard/ →  Show page  →  Done
```

Prevents "Resubmit form?" warning on page refresh.

---

## Troubleshooting

### Error: "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Error: "'OPENWEATHER_API_KEY' not found"
- Create `.env` file
- Add `OPENWEATHER_API_KEY=your_key`
- Restart server

### Error: "Page not found (404)" for static files
Make sure Tailwind CSS CDN is in `base.html` head:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

### Port 8000 already in use
```bash
# Use a different port
python manage.py runserver 8080
```

### Database changes not working
Did you run migrations?
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Next Steps to Improve

Want to extend this app? Here are ideas:

1. **5-day forecasts** - Use OpenWeatherMap's `/forecast` endpoint
2. **User upload profile pictures** - Add `ImageField` to `UserPreference`
3. **Email alerts** - Configure Django's email backend
4. **City search autocomplete** - JavaScript + API autocomplete
5. **Mobile app** - Build React Native frontend using Django REST API
6. **Weather graphs** - Chart.js for temperature history
7. **Dark mode** - Add theme toggle in settings
8. **Multiple countries per city** - Support "New York, US" vs "New York, CA"

---

## Summary

You built a full-stack Django app with:
- User authentication (register/login/logout)
- CRUD operations (add/remove/refresh cities)
- External API integration (OpenWeatherMap)
- Custom models (City, WeatherData, UserPreference, WeatherAlert)
- Alert system with threshold checking
- Beautiful Tailwind CSS UI
- Session-based notifications

**Total lines of code:** ~1,500 lines across:
- 4 models
- 1 service class
- 7 views
- 5 forms
- 8 templates
- 2 URL configs

**Time to build:** ~4-6 hours for a beginner, 1-2 hours for experienced Django dev.

---

**Congratulations on building your first Django weather app!** 🎉

For questions, check Django docs: https://docs.djangoproject.com/
