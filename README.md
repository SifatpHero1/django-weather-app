# WeatherApp - Django Weather Dashboard

A full-featured weather tracking application built with Django. Track weather in multiple cities worldwide, set up smart alerts, and customize your preferences.

---

## Features

### Global Coverage
- Add any city worldwide to your dashboard
- Real-time weather data from OpenWeatherMap API
- Instant updates with one click

### Smart Alerts
- Create custom weather alerts for any tracked city
- Alert types:
  - Temperature above/below threshold
  - Humidity above/below threshold
  - Wind speed above threshold
  - Pressure above/below threshold
- Get notified on dashboard when alerts trigger
- Enable/disable or delete alerts anytime

### Personalized Experience
- Choose temperature units: Celsius, Fahrenheit, Kelvin
- Choose wind speed units: km/h, m/s, mph
- Toggle email notifications
- Set global temperature alert threshold
- Configure auto-refresh intervals (5-120 minutes)

---

## Tech Stack

- **Backend:** Django 5.x
- **API:** OpenWeatherMap
- **Frontend:** HTML, Tailwind CSS, Font Awesome
- **Database:** SQLite (development)

---

## Installation

### Prerequisites
- Python 3.9+
- OpenWeatherMap API key (free at [openweathermap.org](https://openweathermap.org/api))

### Setup Steps

1. **Clone or navigate to the project:**
```bash
cd django_weather_app
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
Create a `.env` file in the project root:
```env
OPENWEATHER_API_KEY=your_api_key_here
```

5. **Apply migrations:**
```bash
python manage.py migrate
```

6. **Create superuser (optional, for admin access):**
```bash
python manage.py createsuperuser
```

7. **Run the development server:**
```bash
python manage.py runserver
```

8. **Open browser:**
```
http://127.0.0.1:8000/
```

---

## Usage Guide

### For Regular Users

1. **Register/Login** - Create an account or sign in
2. **Add Cities** - Click "Add City" or "Global Coverage" on home
   - Enter city name (e.g., "London")
   - Enter country code (e.g., "GB", "US", "BD")
3. **View Dashboard** - See all your cities with current weather
4. **Set Alerts** - Click "Smart Alerts" → Create new alert
   - Select city from your dashboard
   - Choose alert type and threshold
5. **Customize** - Click "Personalized" or "Settings"
   - Change units, enable notifications
   - Set global temperature threshold

### Managing Alerts

- **View all alerts:** `/alerts/`
- **Pause/Resume:** Click play/pause button
- **Delete:** Click trash icon
- **Triggered alerts:** Appear as yellow banners on dashboard after weather refresh

---

## Project Structure

```
django_weather_app/
├── manage.py                  # Django entry point
├── weather_project/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── weather_app/               # Main application
│   ├── models.py             # City, WeatherData, UserPreference, WeatherAlert
│   ├── views.py              # Page logic and API endpoints
│   ├── forms.py              # Registration, login, add city, settings, alerts
│   ├── urls.py               # URL routing
│   ├── services.py           # OpenWeatherMap API integration
│   ├── admin.py              # Admin panel configuration
│   ├── templates/            # HTML templates
│   │   ├── base.html         # Base layout with navbar
│   │   ├── home.html         # Landing page
│   │   ├── dashboard.html    # Main weather display
│   │   ├── add_city.html     # Add new city form
│   │   ├── settings.html     # User preferences
│   │   ├── alerts.html       # Alert management
│   │   ├── login.html        # Login form
│   │   └── register.html     # Registration form
│   └── migrations/           # Database migrations
└── db.sqlite3                # SQLite database
```

---

## API Reference

### WeatherService (`services.py`)

```python
service = WeatherService()

# Get weather for a city (with fallback to demo data)
result = service.get_weather_for_city("London", "GB")

# Geocode city name to coordinates
coords = service.geocode_city("Tokyo", "JP")

# Get demo data (no API key required)
demo = service.get_demo_weather("Paris", "FR")
```

### Views

| URL | Method | Description |
|-----|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard/` | GET | User's weather dashboard |
| `/add_city/` | GET/POST | Add new city |
| `/remove_city/<id>/` | POST | Remove a city |
| `/refresh_weather/<id>/` | POST | Update weather (AJAX) |
| `/settings/` | GET/POST | User preferences |
| `/alerts/` | GET/POST | Manage weather alerts |
| `/alerts/delete/<id>/` | POST | Delete an alert |
| `/alerts/toggle/<id>/` | POST | Enable/disable alert |
| `/register/` | GET/POST | Create account |
| `/login/` | GET/POST | Sign in |
| `/logout/` | POST | Sign out |

---

## Database Models

### City
User's tracked cities with coordinates.

### WeatherData
Current weather for a city (temperature, humidity, wind, etc.).

### UserPreference
User-specific settings (units, refresh interval, notifications).

### WeatherAlert
User-defined alert rules with type, threshold, and active status.

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Yes (or demo mode) |

**Demo Mode:** If no API key is set, the app uses deterministic mock data based on city name (suitable for testing).

---

## Troubleshooting

### "Cannot read Screenshot" error in terminal
This is from your IDE's AI assistant (GH Copilot/Cursor). **Ignore it** or close the AI panel. It's not part of this application.

### Port already in use
```bash
python manage.py runserver 8080
```

### Missing migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### ModuleNotFoundError
Make sure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

---

## Admin Panel

Access at `/admin/` to manage:
- Users
- Cities
- Weather data
- Alerts
- Preferences

---

## Recent Changes (Latest Commit)

**Commit:** `8cdebc8` - Add Smart Alerts feature and enhance personalization

- Added `WeatherAlert` model with 7 alert types
- Created alerts management page with CRUD operations
- Implemented automatic alert checking on weather refresh
- Extended `UserPreference` with email notifications and global temperature threshold
- Updated home page feature boxes to link correctly
- Added alerts link to navigation bar
- Dashboard now shows triggered alert banners

---

## License

This project is open source and available under the MIT License.

---

## Support

For issues or questions, open an issue on the GitHub repository.
