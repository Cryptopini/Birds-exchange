from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name="Home"),
    path('enter', views.enter_view, name="Enter"),
    path('user', views.user_view, name="User"),
    path('logout', views.logout_view, name="Logout"),
    path('chart', views.chart_view, name="Chart"),
    path('orders', views.orders_view, name="Orders")
]
