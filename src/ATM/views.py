from django.shortcuts import render, redirect, get_object_or_404
from .forms import Client_Registration_Form, Custom_Authentication_Form, Delete_Confirmation_Form, Account_Form
from .models import Client, Account, Binnacle, Office_User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from decimal import Decimal

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
                context = {
                    'message': 'Welcome client, We were waiting for you!',
                    'account': accounts
                }
                return render(request, 'ATM/withdraw.html', context)
            else:
                context = {
                    'message': 'Verify your credentials.',
                }
                return render(request, 'ATM/index.html', context)
        except Client.DoesNotExist:
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

def cash_withdrawal(request):
    if request.method == 'POST':
        try:
            denominations = []
            bills_distribution = {}

            account_consulted = Account.objects.get(id=request.POST.get('account_id'))
            card_pin_consulted = account_consulted.card_pin

            if card_pin_consulted == request.POST.get('card_pin'):
                if float(request.POST.get('withdrawal_amount')) > 30000:
                    bills = [10000, 5000, 2000]
                    denominations = bills
                else:
                    bills = [5000, 2000]
                    denominations = bills

                if float(request.POST.get('withdrawal_amount')) < account_consulted.bank_fund:

                    amount = float(request.POST.get('withdrawal_amount'))

                    for denomination in denominations:
                        num_bills = amount // denomination
                        amount %= denomination
                        if num_bills > 0:
                            bills_distribution[denomination] = num_bills

                    if amount > 0:
                        return render(request, 'ATM/withdraw.html', {'message': 'Ha ocurrido un error'})
                    else:
                        account_consulted.bank_fund = account_consulted.bank_fund - Decimal(
                            request.POST.get('withdrawal_amount'))
                        account_consulted.save()
                        context = {
                            'bills_distribution': bills_distribution,
                            'account': [account_consulted],
                        }
                        return render(request, 'ATM/withdraw.html', context)
                else:
                    return render(request, 'ATM/withdraw.html', {'message': 'You dont have that much money in your account.'})
            else:
                return render(request, 'ATM/withdraw.html', {'message': 'This card_pin is incorrect.'})

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
            return render(request, 'ATM/accounts/index.html', {'message': "success acount", 'accounts': accounts, 'form':form})
    else:
        form_account = Account_Form()
        form = Client_Registration_Form()

    return render(request, 'ATM/accounts/index.html', {'form_account': form_account, 'accounts': accounts, 'form':form})