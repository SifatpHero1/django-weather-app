from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import City, UserPreference


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
        fields = ['temperature_unit', 'wind_speed_unit', 'auto_refresh', 'refresh_interval']
        widgets = {
            'temperature_unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'wind_speed_unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}),
            'auto_refresh': forms.CheckboxInput(attrs={'class': 'h-5 w-5 rounded'}),
            'refresh_interval': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': 5,
                'max': 120
            }),
        }
