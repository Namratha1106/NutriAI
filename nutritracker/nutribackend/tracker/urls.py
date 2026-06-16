from django.urls import path
from .views import (
    dashboard, update_water, signup, login_view, reset_password, update_profile, 
    add_meal, get_meals, delete_meal, analyze_image, parse_voice, analytics, assistant
)

urlpatterns = [
    path('dashboard/', dashboard),
    path('update-water/', update_water),
    path('signup/', signup),
    path('login/', login_view),
    path('reset-password/', reset_password),
    path('update-profile/', update_profile),
    path('meals/', get_meals),
    path('add-meal/', add_meal),
    path('delete-meal/', delete_meal),
    path('analyze-image/', analyze_image),
    path('assistant/', assistant),
    path('parse-voice/', parse_voice),
    path('analytics/', analytics),
]