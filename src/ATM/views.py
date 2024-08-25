import logging
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from ATM.utils import log_to_binnacle
from .forms import Client_Registration_Form, Custom_Authentication_Form, Account_Form, Edit_Account_Form
from .models import Client, Account, Binnacle, Office_User

logger = logging.getLogger(__name__)
# Create your views here.

def index(request):
    form = Custom_Authentication_Form()
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ATM/withdraw.html')
    else:
        return render(request, 'ATM/index.html', {'form': form})

def index_admin(request):
    form = Custom_Authentication_Form()
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('register_client')
    else:

        return render(request, 'ATM/Office_User/index_admin.html', {'form': form})

def index_accounts(request):

    accounts = Account.objects.all()
    form = Account_Form()

    return render(request, 'ATM/accounts/index.html', {'accounts': accounts, 'form':form })

@permission_required('ATM.can_manage_clients')
def index_logs(request):
    if not request.user.has_perm('ATM.can_manage_clients'):
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    logs = Binnacle.objects.all()
    return render(request, 'ATM/binnacle/index.html', {'logs': logs })

def index_clients(request):

    clients = Client.objects.all()
    form = Client_Registration_Form()

    return render(request, 'ATM/Office_User/dashboard.html', {'clients': clients, 'form':form})

def verify_user(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:

                client_consulted = Client.objects.get(user__username=username)
                accounts = Account.objects.filter(client=client_consulted)
                log_to_binnacle("User Verified", f"Client {user.client.name} authenticated successfully")
                return render(request, 'ATM/withdraw.html', {'message': 'Welcome client, We were waiting for you!','account': accounts})

            else:

                log_to_binnacle("Failed Login", f"Client {request.POST.get('username')} does not exist")
                return render(request, 'ATM/index.html', {'message': 'Verify your credentials.'})

        except Client.DoesNotExist:
            redirect('home')

def verify_office_user(request):

    form = Custom_Authentication_Form()

    if request.method == 'POST':

        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                log_to_binnacle("User Verified", f"Office_User {user.username} authenticated successfully")
                return redirect('index_clients')
            else:

                log_to_binnacle("Failed Login", f"Office_User {username} or {password} is incorrect or no exist")
                return render(request, 'ATM/Office_User/index_admin.html', {'message': 'This user does not exist.', 'form': form })

        except Office_User.DoesNotExist:
            return redirect('index_admin')

def cash_withdrawal(request):
    if request.method == 'POST':
        try:

            excluded_amounts = {3000, 8000, 11000, 16000, 21000, 27000, 29000}
            bills_distribution = {}

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
                Client.objects.create(user=user)
                log_to_binnacle("Client Register", f"Client {user.username} This user does not exist.")
                return redirect('index_clients')

            except Exception as e:
                return redirect('index_clients')
        else:
            return redirect('index_clients')

def edit_client(request, user_id):

    user = get_object_or_404(User, id=user_id)
    client = get_object_or_404(Client, user=user)
    if request.method == 'POST':
        edit_form = Client_Registration_Form(request.POST, instance=client)
        if edit_form.is_valid():
            edit_form.save()
            client.name = edit_form.cleaned_data['name']
            client.save()
            log_to_binnacle("Failed Edit", f"Client {client.name} has been edit.")
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
            log_to_binnacle("Delete Client", f"Client {user.username} has been delete.")
            client.delete()
            user.delete()
            return redirect('index_clients')


#ACCOUNTS

def create_account(request):

    if request.method == 'POST':
        form_account = Account_Form(request.POST)
        if form_account.is_valid():
            form_account.save()
            log_to_binnacle("Failed Login", f"Client {request.POST.get('client.')} has been delete.")
            return redirect('index_accounts')

        return redirect('index_accounts')

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

def delete_account(request, account_id):

    account = get_object_or_404(Account, id=account_id)

    if request.method == 'POST':
            log_to_binnacle("Delete Account", f"Account the client {account.client.name} has been delete.")
            account.delete()
            return redirect('index_accounts')
