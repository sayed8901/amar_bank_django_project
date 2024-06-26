from django.db import models
from accounts.models import UserBankAccount


all_accounts = UserBankAccount.objects.all()

total_balance = 0
for account in all_accounts:
    total_balance += account.balance


# Create your models here.
class Amar_bank(models.Model):
    bank_name = 'Amar Bank'
    is_bankrupt = models.BooleanField(default = False)

    total_bank_balance = models.IntegerField(default = total_balance)
    