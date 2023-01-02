from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.

class User(AbstractUser):
    pass

class Trade(models.Model):
    #class Meta:
    #    constraints = [models.UniqueConstraint(fields=['user', 'name'], name="unique_name")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=32, null=False, blank=True)
    date = models.DateField(default=date.today)
    DLR_TO = models.DecimalField(decimal_places=4, max_digits=7)
    DLR_U_TO = models.DecimalField(decimal_places=4, max_digits=7)
    buy_FX = models.DecimalField(decimal_places=4, max_digits=5)
    sell_FX = models.DecimalField(decimal_places=4, max_digits=5)
    initial = models.DecimalField(decimal_places=2, max_digits=10)
    initial_fx = models.CharField(choices=(("CAD", "CAD"), ("USD", "USD"), ("TO", "DLR.TO"), ("U", "DLR-U.TO")), default="CAD", max_length=3)
    incur_buy_side_ecn = models.BooleanField()
    incur_sell_side_ecn = models.BooleanField()
    buy_side_ecn = models.DecimalField(decimal_places=4, max_digits=5)
    sell_side_ecn = models.DecimalField(decimal_places=4, max_digits=5)
    buy_side_comm = models.DecimalField(decimal_places=4, max_digits=5)
    sell_side_comm = models.DecimalField(decimal_places=4, max_digits=5)
    lower_bound = models.DecimalField(decimal_places=4, max_digits=5)
    upper_bound = models.DecimalField(decimal_places=4, max_digits=5)
    brokers_spread = models.DecimalField(decimal_places=4, max_digits=5, null=True, blank=True)
    cad_ticker = models.CharField(max_length=8, default="DLR.TO")
    usd_ticker = models.CharField(max_length=8, default="DLR-U.TO")
    closed = models.BooleanField()