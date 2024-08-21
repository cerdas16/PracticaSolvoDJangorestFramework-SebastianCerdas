from django.shortcuts import render, redirect, get_object_or_404
from .forms import Client_Registration_Form, Custom_Authentication_Form, Delete_Confirmation_Form, Account_Form, Edit_Account_Form
from .models import Client, Account, Binnacle, Office_User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from decimal import Decimal
from ATM.utils import log_to_binnacle
import logging

logger = logging.getLogger(__name__)
# Create your views here.

def index(request):
    if request.method == 'POST':
        form = Custom_Authentication_Form(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ATM/withdraw.html')
    else:
        form = Custom_Authentication_Form()

    return render(request, 'ATM/index.html', {'form': form})


def index_admin(request):
    if request.method == 'POST':
        form = Custom_Authentication_Form(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ATM/Office_User/dashboard.html')
    else:
        form = Custom_Authentication_Form()

    return render(request, 'ATM/Office_User/index_admin.html', {'form': form})

def index_accounts(request):

    accounts = Account.objects.all()
    form = Account_Form()

    return render(request, 'ATM/accounts/index.html', {'accounts': accounts, 'form':form })

def index_logs(request):

    logs = Binnacle.objects.all()

    return render(request, 'ATM/binnacle/index.html', {'logs': logs })


def index_clients(request):

    clients = Client.objects.all()
    form = Client_Registration_Form()

    return render(request, 'ATM/Office_User/dashboard.html', {'clients': clients, 'form':form})

@permission_required('ATM.can_manage_clients', raise_exception=True)
def verify_user(request):
    if request.method == 'POST':
        try:
            client_consulted = Client.objects.get(user__username=request.POST.get('username'))

            if check_password(request.POST.get('password'), client_consulted.user.password):
                accounts = Account.objects.filter(client=client_consulted)
                log_to_binnacle("User Verified", f"Client {client_consulted.user.username} authenticated successfully")
                context = {
                    'message': 'Welcome client, We were waiting for you!',
                    'account': accounts
                }
                return render(request, 'ATM/withdraw.html', context)
            else:
                log_to_binnacle("Failed Login", f"Client {request.POST.get('username')} does not exist")
                context = {
                    'message': 'Verify your credentials.',
                }
                return render(request, 'ATM/index.html', context)
        except Client.DoesNotExist:
            log_to_binnacle("Failed Login", f"Client {request.POST.get('username')} This user does not exist.")
            form = Custom_Authentication_Form(request, data=request.POST)
            context = {
                'message': 'This user does not exist.',
                'form': form,
            }
            return render(request, 'ATM/index.html', context)


def verify_office_user(request):

    if request.method == 'POST':
        try:
            office_user_consulted = Office_User.objects.get(user__username=request.POST.get('username'))

            if check_password(request.POST.get('password'), office_user_consulted.user.password):
                clients = Client.objects.all()
                form = Client_Registration_Form(request.POST)
                context = {
                    'message': 'Welcome client, We were waiting for you!',
                    'clients': clients,
                    'form': form
                }
                return render(request, 'ATM/Office_User/dashboard.html', context)
            else:
                context = {
                    'message': 'Verify your credentials.',
                }
                return render(request, 'ATM/Office_User/index_admin.html', context)
        except Office_User.DoesNotExist:
            form = Custom_Authentication_Form(request, data=request.POST)
            context = {
                'message': 'This user does not exist.',
                'form': form,
            }
            return render(request, 'ATM/Office_User/index_admin.html', context)

from decimal import Decimal

def cash_withdrawal(request):
    if request.method == 'POST':
        try:
            # Montos excluidos
            excluded_amounts = {3000, 8000, 11000, 16000, 21000, 27000, 29000}
            denominations = []
            bills_distribution = {}

            # Obtén los datos de la cuenta y PIN
            account_consulted = Account.objects.get(id=request.POST.get('account_id'))
            card_pin_consulted = account_consulted.card_pin
            withdrawal_amount = float(request.POST.get('withdrawal_amount'))

            if card_pin_consulted != request.POST.get('card_pin'):
                return render(request, 'ATM/withdraw.html', {'message': 'This card_pin is incorrect.'})

            if withdrawal_amount in excluded_amounts:
                return render(request, 'ATM/withdraw.html', {'message': 'This amount is not allowed for withdrawal.'})

            if withdrawal_amount > 30000:
                denominations = [10000, 5000, 2000]
            else:
                denominations = [5000, 2000]

            if withdrawal_amount >= account_consulted.bank_fund:
                return render(request, 'ATM/withdraw.html', {'message': 'You dont have that much money in your account.'})

            amount = Decimal(withdrawal_amount)
            for denomination in denominations:
                num_bills = amount // denomination
                amount %= denomination
                if num_bills > 0:
                    bills_distribution[denomination] = num_bills

            if amount > 0:
                return render(request, 'ATM/withdraw.html', {'message': 'Error'})
            else:
                account_consulted.bank_fund -= Decimal(withdrawal_amount)
                account_consulted.save()
                context = {
                    'bills_distribution': bills_distribution,
                    'account': [account_consulted],
                }
                return render(request, 'ATM/withdraw.html', context)

        except Account.DoesNotExist:
            context = {
                'message': 'This account does not exist.',
            }
            return render(request, 'ATM/index.html', context)


def register_client(request):
    if request.method == 'POST':
        form = Client_Registration_Form(request.POST)

        if form.is_valid():
            try:
                user = form.save()

                if not Client.objects.filter(user=user).exists():
                    Client.objects.create(user=user)

                    log_to_binnacle("Failed Login", f"Client {request.POST.get('username')} This user does not exist.")
                    print(f"Client created for user {user.username}")
                else:
                    print(f"Client created for user {user.username}")

                clients = Client.objects.all()
                return render(request, 'ATM/Office_User/dashboard.html', {'clients': clients, 'form': form})

            except Exception as e:
                print(f"Error during registration: {e}")
                form = Client_Registration_Form()
                clients = Client.objects.all()
                return render(request, 'ATM/Office_User/dashboard.html', {'clients': clients, 'form': form})

        else:
            print("Form is invalid")
            print(form.errors)
            clients = Client.objects.all()
            return render(request, 'ATM/Office_User/dashboard.html', {'clients': clients, 'form': form})

    else:
        form = Client_Registration_Form()
        return render(request, 'ATM/Office_User/index_admin.html', {'form': form})


def edit_client(request, user_id):

    user = get_object_or_404(User, id=user_id)
    client = get_object_or_404(Client, user=user)
    if request.method == 'POST':
        edit_form = Client_Registration_Form(request.POST, instance=client)
        if edit_form.is_valid():
            edit_form.save()
            client.name = edit_form.cleaned_data['name']
            client.save()
            log_to_binnacle("Failed Login", f"Client {client.name} has been edit.")
            return render(request, 'ATM/Office_User/dashboard.html', {'edit_form': edit_form, 'user': user})

        else:
            return render(request, 'ATM/Office_User/dashboard.html', {'edit_form': edit_form, 'user': user})

    else:
        edit_form = Client_Registration_Form(instance=client)

    return render(request, 'ATM/Office_User/dashboard.html', {'edit_form': edit_form, 'user': user})

def delete_client(request, client_id):

    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
            user = client.user
            log_to_binnacle("Failed Login", f"Client {user.username} has been delete.")
            client.delete()
            user.delete()
            clients = Client.objects.all()
            form = Client_Registration_Form()
            return render(request, 'ATM/Office_User/dashboard.html',{'clients': clients, 'form':form})

    else:
        return render(request, 'ATM/Office_User/dashboard.html', {'message_delete': "Client Not Delete"})


#ACCOUNTS

def create_account(request):
    accounts = Account.objects.all()
    if request.method == 'POST':
        form_account = Account_Form(request.POST)
        if form_account.is_valid():
            form_account.save()
            form = Client_Registration_Form()
            log_to_binnacle("Failed Login", f"Client {accounts.client.name} has been delete.")
            return render(request, 'ATM/accounts/index.html', {'message': "success acount", 'accounts': accounts, 'form':form})
    else:
        form_account = Account_Form()
        form = Client_Registration_Form()

    return render(request, 'ATM/accounts/index.html', {'form_account': form_account, 'accounts': accounts, 'form':form})


def edit_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    if request.method == 'POST':
        form_edit = Edit_Account_Form(request.POST, instance=account)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('account_list')
    else:
        form_edit = Edit_Account_Form(instance=account)
    return render(request, 'ATM/accounts/index.html', {'form': form_edit, 'account_id': account_id})