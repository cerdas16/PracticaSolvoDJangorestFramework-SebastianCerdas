from django.urls import path
from .views import verify_user, cash_withdrawal, index

urlpatterns = [
    path('', index, name="home"),
    path('/verify_user', verify_user, name="verify_user"),
    path('/cash_withdrawal', cash_withdrawal, name="cash_withdrawal"),
]