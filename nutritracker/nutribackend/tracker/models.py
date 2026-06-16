from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 👤 User Profile (stores goal, height, weight)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calorie_goal = models.IntegerField(default=2000)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)

    def bmi(self):
        if self.height and self.weight:
            return round(self.weight / (self.height ** 2), 2)
        return 0


# 🍽️ Meals
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    protein = models.IntegerField(default=0)
    meal_type = models.CharField(max_length=50, default='Meal')
    meal_time = models.CharField(max_length=50, default='')
    image_url = models.URLField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)


# 💧 Water Tracking
class WaterIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    glasses = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
