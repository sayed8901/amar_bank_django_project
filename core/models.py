from django.db import models
from accounts.models import UserBankAccount
from django.db.models import Sum




all_bank_accounts = UserBankAccount.objects.all()

total_balance = 0
for account in all_bank_accounts:
    total_balance += account.balance



# Create your models here.
class Amar_bank(models.Model):
    bank_name = models.CharField(max_length=100,default='Amar Bank')

    # total_bank_balance = models.DecimalField(decimal_places=2, max_digits=12, default = UserBankAccount.objects.all().aggregate(Sum('balance')))
    total_bank_balance = models.DecimalField(decimal_places=2, max_digits=12, default = total_balance)
    
    is_bankrupt = models.BooleanField(default = False)


    def __str__(self):
        return f'{self.bank_name} - balance: ${self.total_bank_balance} - Is_bankrupt: {self.is_bankrupt}'
