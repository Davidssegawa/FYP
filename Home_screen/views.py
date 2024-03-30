
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
from .models import Meter_Address,Meter_data 
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
#from .serializers import MeterDataSerializer
import json
from django.utils import timezone
import plotly.express as px
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


        return JsonResponse({'message': 'Data received and saved.'})
    else:
        return JsonResponse({'error':'Invalid request method.'}, status=405)
    
# class MeterDataList(APIView):
#     def get(self, request):
#         meter_data = Meter_data.objects.all()
#         serializer = MeterDataSerializer(meter_data, many=True)
#         return Response(serializer.data)
    
def chart_view(request):
    # Retrieve all Meter_data objects from the database
    meter_data = Meter_data.objects.all()
    
    # Prepare data for the line chart
    
    fig = px.line(
        x=[data.timestamp for data in meter_data],
        y=[data.text for data in meter_data],
        title= "Real-time water usage",
        labels = {'x': 'Timestamp','y':'Water measurements'}
    )
    #layout = go.Layout(title='Real time line chart', xaxis={'title': 'timestamp'}, yaxis={'title': 'Water values(L)'})
    # Create a Plotly line chart
    #fig = go.Figure(data=go.Scatter(x=timestamps, y=values, mode='lines'), layout=layout)
    
    chart_html = fig.to_html(full_html=False)
    # Generate the HTML snippet for the chart
    #chart_html = plot(fig, output_type='div', include_plotlyjs=False)
    
    # Render the template with chart HTML
    context = {'chart_html': chart_html}
    return render(request, 'sections\Statistics.html',context )