from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('verify_user', views.verify_user, name="verify_user"),
    path('index_admin', views.index_admin, name="index_admin"),
    path('index_accounts', views.index_accounts, name="index_accounts"),
    path('index_logs', views.index_logs, name="index_logs"),
    path('index_clients', views.index_clients, name="index_clients"),
    path('index_office_users', views.index_office_users, name="index_office_users"),
    path('cash_withdrawal', views.cash_withdrawal, name="cash_withdrawal"),
    path('verify_office_user', views.verify_office_user, name="verify_office_user"),
    path('dashboard', views.register_client, name="register_client"),
    path('edit_client/<int:id>/', views.edit_client, name='edit_client'),
    path('delete_client/<int:client_id>/', views.delete_client, name='delete_client'),
    path('register_account', views.create_account, name="register_account"),
    path('edit_account/<int:id>/', views.edit_account, name='edit_account'),
    path('delete_account/<int:account_id>/', views.delete_account, name='delete_account'),
    path('create_office_user', views.create_office_user, name="create_office_user"),
    path('edit_office_user/<int:id>/', views.edit_office_user, name="edit_office_user"),
    path('delete_office_user/<int:office_user_id>/', views.delete_office_user, name='delete_office_user'),
]
