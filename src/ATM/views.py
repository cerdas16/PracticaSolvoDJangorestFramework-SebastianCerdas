from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .models import client, account, binnacle
from decimal import Decimal

# Create your views here.

def index(request):
    context = {
        'hello':'Hola Mundo',
    }
    return render(request, 'ATM/index.html', context)

def verify_user(request):
    if request.method == 'POST':
        try:
            client_consulted = client.objects.get(username=request.POST.get('username'))

            if client_consulted.username == request.POST.get(
                    'username') and client_consulted.password == request.POST.get('password'):
                accounts = account.objects.filter(client=client_consulted.id)
                context = {
                    'message': 'Welcome client, We were waiting for you!',
                    'account': accounts
                }
                return render(request, 'ATM/withdraw.html', context)

        except client.DoesNotExist:
            context = {
                'message': 'This user does not exist.',
            }
            return render(request, 'ATM/index.html', context)




def cash_withdrawal(request):
    print(f"hola")
    if request.method == 'POST':
        try:
            denominations = []
            bills_distribution = {}

            account_consulted = account.objects.get(id=request.POST.get('account_id'))

            client_consulted = client.objects.get(id=account_consulted.id)

            card_pin_client = client_consulted.card_pin

            if card_pin_client == request.POST.get('card_pin'):
                if float(request.POST.get('withdrawal_amount')) > 30000 :
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
                        bills_distribution[
                            'remaining'] = amount

                    account_consulted.bank_fund = account_consulted.bank_fund - Decimal(request.POST.get('withdrawal_amount'))

                    context = {
                        'bills_distribution': bills_distribution,
                        'account': [account_consulted],
                    }
                    return render(request, 'ATM/withdraw.html', context)
                else:
                    return render(request, 'ATM/withdraw.html', {'message': 'You dont have that much money in your account.'})
            else:
                return render(request, 'ATM/withdraw.html', {'message': 'This card_pin is incorrect.'})

        except account.DoesNotExist:
            context = {
                'message': 'This account does not exist.',
            }
            return render(request, 'ATM/index.html', context)