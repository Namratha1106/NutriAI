from rest_framework import serializers
from .models import Meal, WaterIntake, UserProfile

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'


class WaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterIntake
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_bmi(self, obj):
        return obj.bmi()