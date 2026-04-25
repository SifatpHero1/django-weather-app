from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_city/', views.add_city, name='add_city'),
    path('remove_city/<int:city_id>/', views.remove_city, name='remove_city'),
    path('refresh_weather/<int:city_id>/', views.refresh_weather, name='refresh_weather'),
    path('settings/', views.settings_view, name='settings'),
]
