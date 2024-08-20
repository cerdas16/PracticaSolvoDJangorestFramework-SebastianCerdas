from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Account(models.Model):

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    bank_fund = models.DecimalField(max_digits=40, decimal_places=2)
    card_pin = models.CharField(max_length=4)
    def __str__(self):
        return f"account {self.id}"


class Office_User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Binnacle(models.Model):

    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.action}"