from rest_framework import serializers
from .models import Meter_data,PrepaymentOption,Transaction
from .models import WaterPurchaseTransaction

class MeterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter_data
        fields = ('timestamp', 'text')  # Specify the fields you want to include in the API response


# class WaterUnitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WaterUnit
#         fields = ['id', 'name', 'price']  # Define fields to include in the API response


class PrepaymentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepaymentOption
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class WaterPurchaseTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterPurchaseTransaction
        fields = '__all__'