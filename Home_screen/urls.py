from django.urls import path
from . import views
from .views import AddressView
from .views import MeterDataList,PrepaymentOptionList, TransactionList

urlpatterns =[
    path('',views.index,name='index'),
    path('home/',views.home,name='home'),
    #path('signup',views.signup, name='signup'),
    path('signin/',views.signin,name='signin'),
    path('signout/',views.signout,name='signout'),
    path('home/map/',AddressView.as_view(),name='location'),
    #path('map/',views.map, name='map'),
    path('home/statistics/',views.chart_view,name='statistics'),
    path('home/registermeter/',views.registerMeter,name='registermeter'),
    path('webhook/ttn/', views.ttn_webhook),
    path('api/meter-data/',MeterDataList.as_view(), name='meter-data-list'),
    path('api/prepayment-options/',PrepaymentOptionList.as_view(), name='prepayment-option-list'),
    path('api/transactions/',views.transaction_handler, name='transaction-list')
]
