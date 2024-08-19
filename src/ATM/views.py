from django.shortcuts import render
from django.http import HttpResponse
from models import client, account

# Create your views here.

def index(request):
    context = {
        'hello':'Hola Mundo',
    }
    return render(request, 'ATM/index.html', context)

def verify_user(request):
    client_consulted = client
    if request.method == 'POST':
        client_consulted = client.objects.filter(username__icontains=request.POST.get('username'))

        if client_consulted.username == request.POST.get('username') and client_consulted.password == request.POST.get('password'):
            account_consulted = account.objects.filter(cliente=client_consulted).first()
            context = {
                'message': 'Welcome client, We were waiting for you!',
                'account': account_consulted
            }
            return render(request, 'ATM/withdraw.html', context)
        else:
            context = {
                'message': 'This user does not exist.',
            }
            return render(request, 'ATM/index.html', context)


def cash_withdrawal(request):
    context = {
        'hello':'Hola Mundo',
    }
    return render(request, 'ATM/withdraw.html', context)