from rest_framework import serializers
from .models import Meter_data, WaterUnit

class MeterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter_data
        fields = ('timestamp', 'text')  # Specify the fields you want to include in the API response
class WaterUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUnit
        fields = ['id', 'name', 'price']  # Define fields to include in the API response