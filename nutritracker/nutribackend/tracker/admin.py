from django.contrib import admin
from .models import Meal, WaterIntake, UserProfile

admin.site.register(Meal)
admin.site.register(WaterIntake)
admin.site.register(UserProfile)