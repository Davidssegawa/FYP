# import geocoder
from django.db import models
from django.contrib.auth.models import User
# map_box_access_token = 'pk.eyJ1Ijoic3NlZ2F3YWpvZTgiLCJhIjoiY2xzNjB5YWhsMXJocjJqcGNjazNuenM1dyJ9.oWRkBvrevz2HGD3oWLFdWw'
# Create your models here.

class Meter_Address(models.Model):
    user_id = models.ForeignKey(User, blank=True, default=None, null=True, on_delete=models.CASCADE)
    address = models.TextField()
    lat = models.FloatField(blank=True,null=True)
    long = models.FloatField(blank=True,null=True)


class Meter_data(models.Model):
    meter_id = models.ForeignKey(Meter_Address, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    timestamp = models.DateTimeField()     
    flowRate = models.FloatField( default=0)
    totalMilli = models.FloatField(default=0)
    totalLiters = models.FloatField(default=0)
    totalLitersLeft = models.FloatField(default=0)

    def __str__(self):
        return f"Timestamp: {self.timestamp}, Meter: {self.meter_id}, totalLiters: {self.totalLiters}"

class WaterPurchaseTransaction(models.Model):
    user_id = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL)
    meter_id = models.ForeignKey(Meter_Address, default=None, null=True, on_delete=models.SET_NULL)
    liters_purchased = models.FloatField(default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liters_purchased} liters - {self.timestamp}"
