import geocoder
from django.db import models

map_box_access_token = 'pk.eyJ1Ijoic3NlZ2F3YWpvZTgiLCJhIjoiY2xzNjB5YWhsMXJocjJqcGNjazNuenM1dyJ9.oWRkBvrevz2HGD3oWLFdWw'
# Create your models here.
class Meter_Address(models.Model):
    address = models.TextField()
    lat = models.FloatField(blank=True,null=True)
    long = models.FloatField(blank=True,null=True)

    def save(self,*args,**kwargs):
        g = geocoder.mapbox(self.address, key=map_box_access_token)
        g = g.latlng
        self.lat = g[0]
        self.long = g[1]
        return super(Meter_Address, self).save(*args,**kwargs)


class Meter_data(models.Model):
    timestamp = models.DateTimeField()     
    text = models.FloatField()


    def __str__(self):
        return f"Timestamp: {self.timestamp}, Text: {self.text}"

class WaterUnit(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
