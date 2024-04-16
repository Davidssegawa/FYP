
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

# class TransactionList(generics.ListCreateAPIView):
#     queryset = Transaction.objects.all()
#     serializer_class = TransactionSerializer

# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Disable CSRF protection for this view
def transaction_handler(request):
    if request.method == 'POST':
        try:
            # Decode the incoming JSON data
            data = json.loads(request.body)
            
            # Extract relevant information from the data
            selected_option = data.get('selected_option')
            confirmation_code = data.get('confirmation_code')
            transaction = Transaction.objects.create(selected_option=selected_option, confirmation_code=confirmation_code)
            # Perform any necessary processing or validation
            # For example, save the data to the database
            # transaction = Transaction.objects.create(selected_option=selected_option, confirmation_code=confirmation_code)
            
            # Send back a success response
            return JsonResponse({'message': 'Transaction data received successfully'},status=201)
        except json.JSONDecodeError:
            # If JSON decoding fails, return an error response
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

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






'''from datetime import datetime

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
    data = {
        'Timestamp': [data.timestamp for data in meter_data],
        'Water Measurements': [data.text for data in meter_data]  # Assuming 'value' is the field containing water measurements
    }

    # Create a DataFrame from the data dictionary
    df = pd.DataFrame(data)

    # Extract month from the timestamp
    df['Month'] = pd.to_datetime(df['Timestamp']).dt.month

    # Aggregate water measurements data by month
    aggregated_data = df.groupby('Month')['Water Measurements'].sum().reset_index()

    total_water_consumption = df['Water Measurements'].sum()
    # Create the line chart
    fig_line = px.line(df, x='Timestamp', y='Water Measurements', title="Real-time water usage")

    # Create the pie chart
    fig_pie = px.pie(aggregated_data, names='Month', values='Water Measurements', title='Monthly Water Usage')

    # Create the bar graph
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=aggregated_data['Month'], y=aggregated_data['Water Measurements'], 
                             marker_color='blue', text=aggregated_data['Water Measurements'],
                             textposition='auto', name='Monthly Water Usage'))

    # Convert all plots to HTML
    chart_html_line = fig_line.to_html(full_html=False)
    chart_html_pie = fig_pie.to_html(full_html=False)
    chart_html_bar = fig_bar.to_html(full_html=False)

    context = {
        'chart_html_line': chart_html_line,
        'chart_html_pie': chart_html_pie,
        'chart_html_bar': chart_html_bar,  # New chart
        'total_water_consumption': total_water_consumption,
        'form': form
    }
    return render(request, 'sections/Statistics.html', context)'''


from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    data = {
        'Timestamp': [data.timestamp for data in meter_data],
        'Water Measurements': [data.text for data in meter_data]  # Assuming 'value' is the field containing water measurements
    }

    # Create a DataFrame from the data dictionary
    df = pd.DataFrame(data)

    # Extract day from the timestamp
    df['Day'] = pd.to_datetime(df['Timestamp']).dt.day

    # Aggregate water measurements data by day
    aggregated_data = df.groupby('Day')['Water Measurements'].sum().reset_index()

    total_water_consumption = df['Water Measurements'].sum()

    # Create the line chart
    fig_line = px.line(df, x='Timestamp', y='Water Measurements', title="Real-time water usage")

   # Create the updated pie chart with daily data
    fig_pie_daily = go.Figure(go.Pie(
        labels=aggregated_data['Day'].apply(lambda x: f'Day {x}'),  # Custom labels
        values=aggregated_data['Water Measurements'],
        title='Daily Water Usage',
        textposition='outside',  # Place labels outside the pie chart
    ))

    # Create the bar graph
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=aggregated_data['Day'], y=aggregated_data['Water Measurements'], 
                             marker_color='blue', text=aggregated_data['Water Measurements'],
                             textposition='auto', name='Daily Water Usage'))

    # Convert all plots to HTML
    chart_html_line = fig_line.to_html(full_html=False)
    chart_html_pie_daily = fig_pie_daily.to_html(full_html=False)

    # ... (other code for rendering templates or returning HTTP responses)
    context = {
    'chart_html_line': chart_html_line,
    'chart_html_pie': chart_html_pie_daily,
    # 'chart_html_bar': chart_html_bar,  # New chart
    'total_water_consumption': total_water_consumption,
    'form': form
    }
    return render(request, 'sections/Statistics.html', context)