from django.db import models
from accounts.models import UserBankAccount
from django.db.models import Sum


# Create your models here.
class Amar_bank(models.Model):
    bank_name = models.CharField(max_length=100,default='Amar Bank')
    total_bank_balance = models.IntegerField(default = UserBankAccount.objects.all().aggregate(Sum('balance')))
    
    is_bankrupt = models.BooleanField(default = False)
