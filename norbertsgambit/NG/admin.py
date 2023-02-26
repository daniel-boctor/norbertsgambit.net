from django.contrib import admin

from .models import User, Trade, Portfolio

# Register your models here.

admin.site.register(User)
admin.site.register(Trade)
admin.site.register(Portfolio)