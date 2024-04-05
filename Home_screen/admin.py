from django.contrib import admin
from .models import Meter_Address,Meter_data #,WaterUnit 
# Register your models here.
admin.site.register(Meter_Address)
admin.site.register(Meter_data)
#admin.site.register(WaterUnit)