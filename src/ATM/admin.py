from django.contrib import admin

from .models import account, client, office_user, binnacle

# Register your models here.

admin.site.register(client)
admin.site.register(account)
admin.site.register(office_user)
admin.site.register(binnacle)
