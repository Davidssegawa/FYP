
from datetime import datetime
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
import pandas as pd
from requests import Response
from .models import Meter_Address,Meter_data 
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serializers import MeterDataSerializer
import json
from django.utils import timezone
import plotly.express as px
from .forms import DateRangeForm
from .models import PrepaymentOption, Transaction
from .serializers import PrepaymentOptionSerializer,TransactionSerializer
import plotly.graph_objs as go
#from plotly.graph_objs import scatter


def index(request):
    return render(request,'authentication/index.html')



def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request,username=username, password=pass1)

        if user is not None:
            login(request,user)
            return redirect('home')

        else:
            messages.error(request, 'Wrong credentials')
            return redirect('index')   
         
    return render(request,'authentication/signin.html')

@login_required(login_url='signin')
def home(request):
    return render(request, 'authentication/home.html')

def signout(request):
    logout(request)
    messages.success(request, "Logged out!")
    return redirect("index")

'''@login_required(login_url='signin')
def map(request):
    return render(request,'sections/Map.html')'''

@login_required(login_url='signin')
def statistics(request):
    return render(request,'sections/Statistics.html')

@login_required(login_url='signin')
def registerMeter(request):
    return render(request,'sections/RegisterMeter.html')

#@login_required(login_url='signin')
class AddressView(CreateView):
    model = Meter_Address
    fields = ['address']
    template_name = 'sections/Map.html'
    success_url = '/' 

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['mapbox_access_token'] = 'pk.eyJ1Ijoic3NlZ2F3YWpvZTgiLCJhIjoiY2xzNjB5YWhsMXJocjJqcGNjazNuenM1dyJ9.oWRkBvrevz2HGD3oWLFdWw'
        context["addresses"] = Meter_Address.objects.all()
        return context

@csrf_exempt
def ttn_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)

        timestamp = timezone.now()

        text = data.get("uplink_message",{}).get('decoded_payload',{}).get('text')

        #print("Text:",text)
        #print("Timestamp:",timestamp)

        meter_data = Meter_data(timestamp=timestamp,text=text)
        meter_data.save()

    
class MeterDataList(APIView):
    def get(self, request):
        meter_data = Meter_data.objects.all()
        serializer = MeterDataSerializer(meter_data, many=True)
        return Response(serializer.data)

# class WaterUnitList(APIView):
#     def get(self, request):
#         water_units = WaterUnit.objects.all()
#         serializer = WaterUnitSerializer(water_units, many=True)
#         return Response(serializer.data)   

class PrepaymentOptionList(generics.ListCreateAPIView):
    queryset = PrepaymentOption.objects.all()
    serializer_class = PrepaymentOptionSerializer

class TransactionList(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
# def chart_view(request):
#     # Retrieve all Meter_data objects from the database
#     meter_data = Meter_data.objects.all()
        
#     # Prepare data for the line chart

#     fig = px.line(
#         x=[data.timestamp for data in meter_data],
#         y=[data.text for data in meter_data],
#         title= "Real-time water usage",
#         labels = {'x': 'Timestamp','y':'Water measurements'}

#     )
        
#     chart_html = fig.to_html(full_html=False)
#     context = {'chart_html': chart_html}
#     return render(request, 'sections/Statistics.html',context )
    
from django.utils import timezone
from datetime import timedelta

def chart_view(request):
    form = DateRangeForm(request.GET or None)  # Initialize the form instance
    
    # Retrieve all Meter_data objects from the database
    meter_data = Meter_data.objects.all()

    if form.is_valid():
        start_timestamp = form.cleaned_data.get('start_timestamp')
        end_timestamp = form.cleaned_data.get('end_timestamp')

        if start_timestamp:
            meter_data = meter_data.filter(timestamp__gte=start_timestamp)
        if end_timestamp:
            meter_data = meter_data.filter(timestamp__lte=end_timestamp)

    meter_data = meter_data.order_by('timestamp')
    
    # Calculate the start and end timestamps for each 24-hour interval
    start_date = min(meter_data.values_list('timestamp', flat=True))
    end_date = max(meter_data.values_list('timestamp', flat=True))
    intervals = []
    current_date = start_date
    while current_date < end_date:
        intervals.append((current_date, current_date + timedelta(days=1)))
        current_date += timedelta(days=1)

    # Aggregate water measurements data for each 24-hour interval
    aggregated_data = []
    for interval in intervals:
        start_interval, end_interval = interval
        water_measurements_sum = meter_data.filter(timestamp__gte=start_interval, timestamp__lt=end_interval).aggregate(Sum('water_measurements'))['water_measurements__sum']
        aggregated_data.append({'Interval': start_interval.strftime('%Y-%m-%d'), 'Water Measurements': water_measurements_sum or 0})

    # Convert aggregated data to DataFrame
    df = pd.DataFrame(aggregated_data)

    # Create the line chart
    fig_line = px.line(df, x='Interval', y='Water Measurements', title="Real-time water usage")

    # Create the pie chart
    fig_pie = px.pie(df, names='Interval', values='Water Measurements', title='Daily Water Usage')

    # Convert plots to HTML
    chart_html_line = fig_line.to_html(full_html=False)
    chart_html_pie = fig_pie.to_html(full_html=False)

    context = {
        'chart_html_line': chart_html_line,
        'chart_html_pie': chart_html_pie,
        'form': form
    }
    return render(request, 'sections/Statistics.html', context)
