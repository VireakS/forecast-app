
from rest_framework import serializers
from .models import ForecastModel


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastModel
        fields = '__all__'