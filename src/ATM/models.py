from django.db import models
from django.utils import timezone
# Create your models here.

class client(models.Model):

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    card_pin = models.CharField(max_length=4)

    def __str__(self):
        return self.card_pin


class account(models.Model):

    client = models.ForeignKey(client, on_delete=models.CASCADE)
    bank_fund = models.DecimalField(max_digits=40, decimal_places=2)
    def __str__(self):
        return f"account {self.id}"

class office_user(models.Model):

    username = models.CharField(max_length=20)
    password = models.CharField(max_length=50)

class binnacle(models.Model):

    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.action}"