from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import City, UserPreference, WeatherAlert


# Authentication Forms
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
    }))


# App Forms
class AddCityForm(forms.Form):
    """Form for adding a new city to track weather"""
    city_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter city name (e.g., London)',
            'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
        })
    )
    country_code = forms.CharField(
        max_length=2,
        initial='US',
        widget=forms.TextInput(attrs={
            'placeholder': 'Country code (e.g., US, GB, BD)',
            'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        city_name = cleaned_data.get('city_name')
        country_code = cleaned_data.get('country_code')

        if city_name and country_code and self.user:
            # Check for duplicate city for this user (case-insensitive)
            if City.objects.filter(
                user=self.user,
                name__iexact=city_name,
                country_code__iexact=country_code
            ).exists():
                raise forms.ValidationError(
                    f"You already have {city_name}, {country_code} in your list."
                )
        return cleaned_data


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['temperature_unit', 'wind_speed_unit', 'auto_refresh', 'refresh_interval', 'email_notifications', 'temperature_alert_threshold']
        widgets = {
            'temperature_unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'wind_speed_unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'auto_refresh': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded'}),
            'refresh_interval': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': 5,
                'max': 120
            }),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded'}),
            'temperature_alert_threshold': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'step': '0.1',
                'placeholder': 'e.g., 35 for hot alerts, -5 for cold alerts'
            }),
        }


class AlertForm(forms.Form):
    """Form for creating weather alerts"""
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'City name (must be in your dashboard)',
            'class': 'w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/30'
        })
    )
    alert_type = forms.ChoiceField(
        choices=WeatherAlert.ALERT_TYPES,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'})
    )
    threshold_value = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
            'step': '0.1'
        }),
        help_text="Enter threshold value (e.g., 35 for temperature above 35°C)"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        city_name = cleaned_data.get('city')
        
        if city_name and self.user:
            # Check if city exists in user's dashboard
            if not City.objects.filter(user=self.user, name__iexact=city_name).exists():
                raise forms.ValidationError(
                    f"You must add {city_name} to your dashboard first before creating an alert."
                )
        return cleaned_data
