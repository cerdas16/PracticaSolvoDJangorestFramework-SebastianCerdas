from django.contrib import admin

from .models import Account, Client, Office_User, Binnacle

# Register your models here.

admin.site.register(Client)
admin.site.register(Account)
admin.site.register(Office_User)
admin.site.register(Binnacle)
