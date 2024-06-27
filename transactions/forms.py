from django import forms
from .models import Transaction
from core.models import Amar_bank

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type',]
    

    # user er account ta ekhane pass kore dibo
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # (views theke) account value ke pop kore anlam

        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    
    # function to save transaction activity
    def save(self, commit=True):
        self.instance.account = self.account # current account object hishebe ektu age __init__ function theke capture kora account ke ekhane die dibo 

        self.instance.balance_after_transaction = self.account.balance  # je kono type er transaction (eg: deposit, loan or withdrawal) hober pore sei new amount balance die tar account er balance_after_transaction ke update kore dicchi

        return super().save() # finally, parent ke overwrite kore tar account amd updated balance save kore dicchi
    



class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100

        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount




class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account

        min_withdraw_amount = 500
        max_withdraw_amount = 20000

        balance = account.balance 

        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam


        bank = Amar_bank.objects.get(bank_name='Amar Bank')
        print(bank)
        # print(bank.is_bankrupt)

        if bank.is_bankrupt:
            raise forms.ValidationError(
                f"You can not withdraw any amount from this bank as '{bank.bank_name}' has been declared as bankrupt."
            )
        else:
            if amount < min_withdraw_amount:
                raise forms.ValidationError(
                    f'You can withdraw at least {min_withdraw_amount} $'
                )

            if amount > max_withdraw_amount:
                raise forms.ValidationError(
                    f'You can withdraw at most {max_withdraw_amount} $'
                )

            if amount > balance: 
                raise forms.ValidationError(
                    f'You have {balance} $ in your account.'
                    'You can not withdraw more than your account balance'
                )         
        

        return amount





class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam

        return amount
    




# Money transfer form
class MoneyTransferForm(TransactionForm):
    account_number = forms.IntegerField()

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount']

