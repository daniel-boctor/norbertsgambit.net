from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from datetime import date

# Create your models here.

class User(AbstractUser):
    pass

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Trade(models.Model):
    #class Meta:
    #    constraints = [models.UniqueConstraint(fields=['user', 'name'], name="unique_name")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=32, null=False, blank=True)
    date = models.DateField(default=date.today)
    DLR_TO = models.DecimalField(decimal_places=4, max_digits=9, validators=[MinValueValidator(0.01)])
    DLR_U_TO = models.DecimalField(decimal_places=4, max_digits=9, validators=[MinValueValidator(0.01)])
    buy_FX = models.DecimalField(decimal_places=4, max_digits=7, validators=[MinValueValidator(0.01)])
    sell_FX = models.DecimalField(decimal_places=4, max_digits=7, validators=[MinValueValidator(0.01)])
    initial = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0.01)])
    initial_fx = models.CharField(choices=(("CAD", "CAD"), ("USD", "USD"), ("TO", "DLR.TO"), ("U", "DLR-U.TO")), default="CAD", max_length=3)
    incur_buy_side_ecn = models.BooleanField(default=False)
    incur_sell_side_ecn = models.BooleanField(default=True)
    buy_side_ecn = models.DecimalField(decimal_places=4, default='0.0035', max_digits=7, validators=[MinValueValidator(0)])
    sell_side_ecn = models.DecimalField(decimal_places=4, default='0.0035', max_digits=7, validators=[MinValueValidator(0)])
    buy_side_comm = models.DecimalField(decimal_places=4, default='0.00', max_digits=7, validators=[MinValueValidator(0)])
    sell_side_comm = models.DecimalField(decimal_places=4, default='0.01', max_digits=7, validators=[MinValueValidator(0)])
    lower_bound = models.DecimalField(decimal_places=4, default='4.95', max_digits=7, validators=[MinValueValidator(0)])
    upper_bound = models.DecimalField(decimal_places=4, default='9.95', max_digits=7, validators=[MinValueValidator(0)])
    brokers_spread = models.DecimalField(decimal_places=4, max_digits=6, null=True, blank=True, validators=[MinValueValidator(0)])
    dealers_rate = models.DecimalField(decimal_places=4, max_digits=6, null=True, blank=True, validators=[MinValueValidator(0.01)])
    cad_ticker = models.CharField(max_length=8, default="DLR.TO")
    usd_ticker = models.CharField(max_length=8, default="DLR-U.TO")
    closed = models.BooleanField()