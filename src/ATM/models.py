from django.db import models

# Create your models here.

class client(models.Model):

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    card_pin = models.CharField(max_length=4)

class account(models.Model):

    client = models.ForeignKey(client, on_delete=models.CASCADE)
    bank_fund = models.DecimalField(max_digits=40, decimal_places=2)

class office_user(models.Model):

    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)

class binnacle(models.Model):

    account = models.ForeignKey(account, on_delete=models.CASCADE)
    withdrawal_amount = models.CharField(max_length=20)
    password = models.CharField(max_length=50)