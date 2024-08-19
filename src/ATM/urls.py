from django.urls import path

from ATM import views

urlpatterns = [
    path('', views.index, name="index" ),
]