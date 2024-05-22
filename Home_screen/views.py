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
from .models import Meter_Address,Meter_data, WaterPurchaseTransaction 
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serializers import MeterDataSerializer
import json
from django.utils import timezone
import plotly.express as px
from .forms import DateRangeForm
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objs as go
import time
from .downlink import schedule_downlink, TTN_API_KEY, APPLICATION_ID, DEVICE_ID

def index(request):
    if request.method == "POST":
        email = request.POST['email']
        pass1 = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request,username=user.username, password=pass1)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong credentials')
            return redirect('signin')   
         
    return render(request,'authentication/signin.html')

@login_required(login_url='')
def home(request):
    print(request.GET.get('meter', None))
    if request.user.is_staff:
            context = dict()
            context['mapbox_access_token'] = 'pk.eyJ1Ijoic3NlZ2F3YWpvZTgiLCJhIjoiY2xzNjB5YWhsMXJocjJqcGNjazNuenM1dyJ9.oWRkBvrevz2HGD3oWLFdWw'
            context["addresses"] = [[address.long, address.lat, address.id] for address in Meter_Address.objects.all()]
            # form = DateRangeForm(request.GET or None)  # Initialize the form instance
            # context['form'] = form
            meter_id = request.GET.get('meter', None)
            if meter_id:
                meter = Meter_Address.objects.get(pk=int(meter_id))
                if meter:
                    meter_data = meter.meter_data_set.all()
                    meter_data = meter_data.order_by('timestamp')[:50]
                    data = {
                        'Timestamp': [data.timestamp for data in meter_data],
                        'Water Measurements': [data.totalLiters for data in meter_data]  # Assuming 'value' is the field containing water measurements
                    }

                    # Create a DataFrame from the data dictionary
                    df = pd.DataFrame(data)

                    # Extract day from the timestamp
                    df['Date'] = pd.to_datetime(df['Timestamp']).dt.date

                    # Aggregate water measurements data by day
                    aggregated_data = df.groupby('Date')['Water Measurements'].sum().reset_index()

                    total_water_consumption = df['Water Measurements'].sum()

                    # Create the line chart
                    fig_line = px.line(df, x='Timestamp', y='Water Measurements', title="Real-time water usage",labels={'Timestamp': 'Timestamp', 'Water Measurements': 'Daily water usage (Liters)'})

                # Create the updated pie chart with daily data
                    fig_pie_daily = go.Figure(go.Pie(
                        labels=aggregated_data['Date'].apply(lambda x: f'Date {x}'),  # Custom labels
                        values=aggregated_data['Water Measurements'],
                        title='Daily Water Usage',title_font_size=20,
                        textposition='outside',  # Place labels outside the pie chart
                    ))

                    # Create the bar graph for daily water usage
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=aggregated_data['Date'].apply(lambda x: x.strftime('%Y-%m-%d')), 
                        y=aggregated_data['Water Measurements'], 
                        text=aggregated_data['Date'].apply(lambda x: f'Date {x.strftime("%Y-%m-%d")}'),  # Custom text for each bar
                        hovertext=aggregated_data['Date'].apply(lambda x: f'Date: {x.strftime("%Y-%m-%d")}<br>Water Usage: {x} liters'),  # Custom hover text
                        marker_color='blue',
                        textposition='auto',
                        name='Daily Water Usage'
                    ))
                    fig_bar.update_layout(
                        title="Daily Water Usage",
                        xaxis_title="Date",
                        yaxis_title="Total daily water consumption (Liters)"
                    )

                    # Convert all plots to HTML
                    chart_html_line = fig_line.to_html(full_html=False)
                    chart_html_pie_daily = fig_pie_daily.to_html(full_html=False)

                    # ... (other code for rendering templates or returning HTTP responses)
                    context['chart_html_line'] = chart_html_line
                    context['chart_html_pie'] = chart_html_pie_daily
                    context['chart_html_bar'] =fig_bar.to_html(full_html=False) # New chart
                    context['total_water_consumption'] = round(total_water_consumption,3)
                        # 'form': form
            return render(request, 'authentication/home.html', context=context)
    user = User.objects.get(pk=request.user.id)
    print(user)
    context = dict()
    if user:
        meter = Meter_Address.objects.get(user_id=user)
        # if meter_id:
            # meter = Meter_Address.objects.get(pk=int(meter_id))
        if meter:
            meter_data = meter.meter_data_set.all()
            meter_data = meter_data.order_by('timestamp')[:50]
            data = {
                'Timestamp': [data.timestamp for data in meter_data],
                'Water Measurements': [data.totalLiters for data in meter_data]  # Assuming 'value' is the field containing water measurements
            }

            # Create a DataFrame from the data dictionary
            df = pd.DataFrame(data)

            # Extract day from the timestamp
            df['Date'] = pd.to_datetime(df['Timestamp']).dt.date

            # Aggregate water measurements data by day
            aggregated_data = df.groupby('Date')['Water Measurements'].sum().reset_index()

            total_water_consumption = df['Water Measurements'].sum()
            averaged_value = df['total_water_consumption'].average()
            estimated_cost_monthly = (averaged_value*4224)/1000
            # Create the line chart
            fig_line = px.line(df, x='Timestamp', y='Water Measurements', title="Real-time water usage",labels={'Timestamp': 'Timestamp', 'Water Measurements': 'Real-time daily water usage(Liters)'})

        # Create the updated pie chart with daily data
            fig_pie_daily = go.Figure(go.Pie(
                labels=aggregated_data['Date'].apply(lambda x: f'Date {x}'),  # Custom labels
                values=aggregated_data['Water Measurements'],
                title='Daily Water Usage',
                textposition='outside',  # Place labels outside the pie chart
            ))

            # Create the bar graph for daily water usage
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=aggregated_data['Date'].apply(lambda x: x.strftime('%Y-%m-%d')), 
                y=aggregated_data['Water Measurements'], 
                text=aggregated_data['Date'].apply(lambda x: f'Date {x.strftime("%Y-%m-%d")}'),  # Custom text for each bar
                hovertext=aggregated_data['Date'].apply(lambda x: f'Date: {x.strftime("%Y-%m-%d")}<br>Water Usage: {x} liters'),  # Custom hover text
                marker_color='blue',
                textposition='auto',
                name='Daily Water Usage'
            ))
            fig_bar.update_layout(
                title="Daily Water Usage",
                xaxis_title="Date",
                yaxis_title="Total daily water consumption (Liters)"
            )

            # Convert all plots to HTML
            chart_html_line = fig_line.to_html(full_html=False)
            chart_html_pie_daily = fig_pie_daily.to_html(full_html=False)

            # ... (other code for rendering templates or returning HTTP responses)
            context['chart_html_line'] = chart_html_line
            context['chart_html_pie'] = chart_html_pie_daily
            context['chart_html_bar'] =fig_bar.to_html(full_html=False) # New chart
            context['total_water_consumption'] = round(total_water_consumption,3)
            total_purchased = sum([val['liters_purchased'] for val in meter.waterpurchasetransaction_set.values('liters_purchased')])
            total_used = sum([val['totalLiters'] for val in meter.meter_data_set.values('totalLiters')])
            context['total_water_current'] = round(total_purchased - total_used, 3)
            context['Estimated_monthly_cost'] = round(estimated_cost_monthly)
            # print(context)
    return render(request, 'authentication/user_home.html', context=context)

def signout(request):
    logout(request)
    messages.success(request, "Logged out!")
    return redirect("signin")


@login_required(login_url='')
def registerMeter(request):
    if request.method == "POST":
        print(request.POST)
        email = request.POST.get('email', None)
        if email:
            try:
                user_exists = User.objects.get(email=email)
            except:
                user_exists = None
            if user_exists:
                messages.error(request,'User already exists')
                return redirect('registermeter')
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)

            if username and password:
                user = None
                try:
                    user = User.objects.create_user(username, email, password)
                except:
                    messages.error(request, "Password too short, should be 8 characters atleast")
                    return redirect('registermeter')
                latitude = request.POST.get('latitude', None)
                longitude = request.POST.get('longitude', None)

                if latitude and longitude and user:
                    address = f"Lat:{latitude} Long:{longitude}"
                    meter = Meter_Address.objects.create(user_id=user, address=address, lat=float(latitude), long=float(longitude))

                    messages.success(request, "User and meter successfully registered")
                    return redirect('registermeter')
        
    return render(request,'sections/RegisterMeter.html')

@login_required(login_url='')
def purchase(request):
    if request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        print(request.POST)
        time.sleep(5)
        # messages.success(request, "Transaction successful")
        print(request.user.meter_address_set.all()[0])
        user_id = request.user
        meter_id = request.user.meter_address_set.all()[0]
        amount_paid = float(request.POST.get('amount', None))
        if amount_paid > 0:
            liters_purchased = (amount_paid/4224)*1000
            try:
                purchase_order = WaterPurchaseTransaction.objects.create(user_id=user_id, meter_id=meter_id, amount_paid=amount_paid, liters_purchased=liters_purchased)
                print(purchase_order)
            except:
                messages.error(request, "Transaction unsuccessful. Try again later")
                return render(request, 'sections/purchase.html')
            
            try:
                response = schedule_downlink(DEVICE_ID, int(liters_purchased), 1, APPLICATION_ID, TTN_API_KEY)
                print(response)
            except:
                messages.error(request, "Downlink unsuccessful")
            messages.success(request, "Transaction successful")
            return render(request, 'sections/purchase.html')
    return render(request, 'sections/purchase.html')

@csrf_exempt
def ttn_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)

        timestamp = timezone.now()

        text = data.get("uplink_message",{}).get('decoded_payload',{}).get('text1')

        flow_rate, total_milliliters, total_liters, total_liters_left = text.split(',')

        print(flow_rate, total_milliliters, total_liters, total_liters_left)

        meter_data = Meter_data(timestamp=timestamp,flowRate=flow_rate, totalMilli=total_milliliters, totalLiters=total_liters, totalLitersLeft=total_liters_left)
        meter_data.save()

