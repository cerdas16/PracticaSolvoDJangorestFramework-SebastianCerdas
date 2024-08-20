from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('/verify_user', views.verify_user, name="verify_user"),
    path('/index_admin', views.index_admin, name="index_admin"),
    path('/cash_withdrawal', views.cash_withdrawal, name="cash_withdrawal"),
]